"""
Tool Factory

Tạo tools theo Factory Pattern.
"""

from app.chemistry.rdkit_tool import RDKitTool


class ToolFactory:
    """
    Factory để tạo tools.
    
    Cho phép swap tools mà không thay đổi pipeline code.
    """
    
    @staticmethod
    def create_chemistry_tool() -> RDKitTool:
        """
        Tạo chemistry tool (RDKit).
        
        Returns:
            RDKitTool instance
        """
        return RDKitTool()
    
    @staticmethod
    def create_tool(tool_type: str):
        """
        Generic factory method.
        
        Args:
            tool_type: Loại tool ("chemistry", etc.)
            
        Returns:
            Tool instance
            
        Raises:
            ValueError: Nếu tool_type không hợp lệ
        """
        if tool_type == "chemistry":
            return ToolFactory.create_chemistry_tool()
        else:
            raise ValueError(f"Unknown tool type: {tool_type}")
