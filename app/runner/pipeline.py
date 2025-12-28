"""
Agentic Pipeline

Orchestrates multi-round agentic loop cho molecule generation và screening.

Flow:
    1. Planner định nghĩa strategy
    2. Loop qua các rounds:
        a. Generator đề xuất candidates
        b. Chemistry tool validate và compute properties
        c. Screening filter molecules
        d. Ranker chọn top molecules
    3. Top molecules từ round N seed cho round N+1
"""

from typing import Dict, Any, List, Optional
import logging
from app.factories.agent_factory import AgentFactory
from app.factories.tool_factory import ToolFactory
from app.screening.rules import MoleculeScreening
from app.trace.tracer import get_tracer
from app.db.session import get_db_session
from app.db.models import Run, Molecule, TraceEvent
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AgenticPipeline:
    """
    Pipeline orchestrator cho agentic molecule generation.
    
    KHÔNG BAO GIỜ instantiate agents/tools trực tiếp.
    LUÔN sử dụng factories.
    """
    
    def __init__(self):
        self.tracer = get_tracer()
    
    def run(self, run_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agentic pipeline.
        
        Args:
            run_id: Run ID
            parameters: Run parameters từ planner
            
        Returns:
            Dictionary chứa results
        """
        db = get_db_session()
        
        try:
            # Update run status
            run = db.query(Run).filter(Run.id == run_id).first()
            run.status = "running"
            run.started_at = datetime.utcnow()
            run.progress_message = "Initializing pipeline..."
            db.commit()
            
            logger.info(f"="*60)
            logger.info(f"🚀 STARTING PIPELINE - Run ID: {run_id}")
            logger.info(f"="*60)
            logger.info(f"Parameters: {parameters}")
            
            # Log start
            self.tracer.log(
                actor="pipeline",
                action="Starting agentic pipeline",
                run_id=run_id,
                metadata=parameters
            )
            
            # Create agents via factories
            logger.info("📋 Creating agents via factories...")
            run.progress_message = "Creating agents..."
            db.commit()
            
            planner = AgentFactory.create_planner(**parameters)
            generator = AgentFactory.create_generator()
            ranker = AgentFactory.create_ranker()
            logger.info("   ✅ Planner, Generator, Ranker created")
            
            # Create tools via factories
            chemistry_tool = ToolFactory.create_chemistry_tool()
            logger.info("   ✅ Chemistry tool created")
            
            # Get plan
            logger.info("📝 Planner generating run strategy...")
            run.progress_message = "Planning strategy..."
            db.commit()
            
            plan = planner.act(parameters)
            logger.info(f"   ✅ Plan: {plan['rounds']} rounds, {plan['candidates_per_round']} candidates/round, top-{plan['top_k']}")
            self.tracer.log_agent_action(
                agent_name="planner",
                action="Generated run plan",
                run_id=run_id,
                result=plan
            )
            
            # Extract parameters
            rounds = plan["rounds"]
            candidates_per_round = plan["candidates_per_round"]
            top_k = plan["top_k"]
            max_violations = plan["max_violations"]
            scoring_penalty = plan["scoring_penalty"]
            
            # Initialize screening
            screening = MoleculeScreening(max_violations=max_violations)
            
            # Multi-round loop
            seed_molecules = []
            all_molecules = []
            
            for round_num in range(1, rounds + 1):
                logger.info(f"\n{'='*60}")
                logger.info(f"🔄 ROUND {round_num}/{rounds}")
                logger.info(f"{'='*60}")
                
                # Update progress
                run.current_round = round_num
                run.progress_message = f"Round {round_num}/{rounds}: Generating candidates..."
                db.commit()
                
                self.tracer.log(
                    actor="pipeline",
                    action=f"Starting round {round_num}/{rounds}",
                    run_id=run_id,
                    round_num=round_num
                )
                
                # Generate candidates
                logger.info(f"🧬 Generator proposing {candidates_per_round} molecules...")
                gen_context = {
                    "n_candidates": candidates_per_round,
                    "round_num": round_num,
                    "seed_molecules": [m["smiles"] for m in seed_molecules]
                }
                gen_result = generator.act(gen_context)
                candidates = gen_result["candidates"]
                logger.info(f"   ✅ Generated {len(candidates)} candidates")
                
                self.tracer.log_agent_action(
                    agent_name="generator",
                    action=f"Generated {len(candidates)} candidates",
                    run_id=run_id,
                    round_num=round_num,
                    result={"n_candidates": len(candidates)}
                )
                
                # Process molecules với chemistry tool
                logger.info(f"⚗️  Chemistry tool validating & computing properties...")
                run.progress_message = f"Round {round_num}/{rounds}: Computing properties..."
                db.commit()
                
                processed_molecules = []
                valid_count = 0
                
                for idx, smiles in enumerate(candidates, 1):
                    if idx % 10 == 0:
                        logger.info(f"   Processing {idx}/{len(candidates)}...")
                    result = chemistry_tool.process_molecule(smiles)
                    
                    if result["valid"]:
                        valid_count += 1
                        # Screen molecule
                        properties = result["properties"]
                        eval_result = screening.evaluate_molecule(
                            properties,
                            penalty=scoring_penalty
                        )
                        
                        mol_data = {
                            "smiles": smiles,
                            "valid": True,
                            "round": round_num,
                            "properties": properties,
                            "screening_result": eval_result["screening_result"],
                            "score": eval_result["score"]
                        }
                        
                        # Only keep molecules that pass screening
                        if eval_result["screening_result"]["passed"]:
                            processed_molecules.append(mol_data)
                
                logger.info(f"   ✅ Validated: {valid_count}/{len(candidates)} molecules")
                
                self.tracer.log_tool_action(
                    tool_name="chemistry",
                    action=f"Processed {len(candidates)} molecules, {valid_count} valid",
                    run_id=run_id,
                    round_num=round_num,
                    count=valid_count
                )
                
                logger.info(f"🔬 Screening with Lipinski rules (max violations: {max_violations})...")
                run.progress_message = f"Round {round_num}/{rounds}: Screening molecules..."
                db.commit()
                
                logger.info(f"   ✅ Passed screening: {len(processed_molecules)} molecules")
                
                self.tracer.log_tool_action(
                    tool_name="screening",
                    action=f"Filtered to {len(processed_molecules)} passing molecules",
                    run_id=run_id,
                    round_num=round_num,
                    count=len(processed_molecules)
                )
                
                # Rank molecules
                logger.info(f"🏆 Ranker scoring and selecting top molecules...")
                run.progress_message = f"Round {round_num}/{rounds}: Ranking molecules..."
                db.commit()
                
                rank_context = {
                    "molecules": processed_molecules,
                    "scoring_penalty": scoring_penalty,
                    "top_k": top_k
                }
                rank_result = ranker.act(rank_context)
                ranked_molecules = rank_result["ranked_molecules"]
                top_molecules = rank_result["top_molecules"]
                
                logger.info(f"   ✅ Ranked {len(ranked_molecules)} molecules")
                logger.info(f"   🥇 Selected top {len(top_molecules)} for next round")
                if top_molecules:
                    logger.info(f"   🎯 Best score this round: {top_molecules[0]['score']:.4f}")
                
                self.tracer.log_agent_action(
                    agent_name="ranker",
                    action=f"Ranked {len(ranked_molecules)} molecules, selected top {len(top_molecules)}",
                    run_id=run_id,
                    round_num=round_num,
                    result={"n_ranked": len(ranked_molecules), "n_top": len(top_molecules)}
                )
                
                # Store molecules
                all_molecules.extend(ranked_molecules)
                
                # Update seeds cho round tiếp theo
                seed_molecules = top_molecules
            
            # Assign final ranks
            logger.info(f"\n{'='*60}")
            logger.info(f"📊 FINALIZING RESULTS")
            logger.info(f"{'='*60}")
            
            run.progress_message = "Finalizing results..."
            db.commit()
            
            all_molecules_sorted = sorted(all_molecules, key=lambda x: x["score"], reverse=True)
            for idx, mol in enumerate(all_molecules_sorted):
                mol["rank"] = idx + 1
            
            logger.info(f"💾 Saving {len(all_molecules_sorted)} molecules to database...")
            
            # Save to database
            for mol in all_molecules_sorted:
                db_mol = Molecule(
                    run_id=run_id,
                    smiles=mol["smiles"],
                    valid=mol["valid"],
                    round=mol["round"],
                    properties=mol["properties"],
                    screening_result=mol["screening_result"],
                    score=mol["score"],
                    rank=mol["rank"]
                )
                db.add(db_mol)
            
            # Save trace events
            for event in self.tracer.get_events(run_id):
                db_event = TraceEvent(
                    run_id=run_id,
                    actor=event["actor"],
                    action=event["action"],
                    round=event["round"],
                    event_metadata=event["metadata"],
                    timestamp=datetime.fromisoformat(event["timestamp"])
                )
                db.add(db_event)
            
            # Update run status
            run.status = "completed"
            run.completed_at = datetime.utcnow()
            run.current_round = rounds
            run.progress_message = "Completed successfully"
            db.commit()
            
            logger.info(f"\n{'='*60}")
            logger.info(f"✅ PIPELINE COMPLETED SUCCESSFULLY")
            logger.info(f"{'='*60}")
            logger.info(f"📈 Total molecules generated: {len(all_molecules_sorted)}")
            if all_molecules_sorted:
                logger.info(f"🏆 Top score: {all_molecules_sorted[0]['score']:.4f}")
                logger.info(f"🧬 Top molecule: {all_molecules_sorted[0]['smiles']}")
            logger.info(f"⏱️  Duration: {(run.completed_at - run.started_at).total_seconds():.2f}s")
            logger.info(f"={'='*60}\n")
            
            self.tracer.log(
                actor="pipeline",
                action="Pipeline completed successfully",
                run_id=run_id,
                metadata={
                    "total_molecules": len(all_molecules_sorted),
                    "top_score": all_molecules_sorted[0]["score"] if all_molecules_sorted else None
                }
            )
            
            return {
                "status": "completed",
                "molecules": all_molecules_sorted,
                "total": len(all_molecules_sorted)
            }
            
        except Exception as e:
            # Handle error
            logger.error(f"\n{'='*60}")
            logger.error(f"❌ PIPELINE FAILED")
            logger.error(f"{'='*60}")
            logger.error(f"Error: {str(e)}", exc_info=True)
            logger.error(f"={'='*60}\n")
            
            run.status = "failed"
            run.error_message = str(e)
            run.completed_at = datetime.utcnow()
            run.progress_message = f"Failed: {str(e)}"
            db.commit()
            
            self.tracer.log(
                actor="pipeline",
                action=f"Pipeline failed: {str(e)}",
                run_id=run_id
            )
            
            return {
                "status": "failed",
                "error": str(e)
            }
            
        finally:
            db.close()
