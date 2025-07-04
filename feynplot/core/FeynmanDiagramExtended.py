# Ensure necessary classes and modules are imported
from typing import List, Tuple, Dict, Any, Optional

from feynplot.core.vertex import Vertex
from feynplot.core.line import Line, FermionLine, AntiFermionLine, PhotonLine, GluonLine, WPlusLine, WMinusLine, ZBosonLine
from feynplot.core.diagram import FeynmanDiagram # Import the base class

# Define a simple class for text elements
class TextElement:
    def __init__(self, text: str, x: float, y: float, **kwargs):
        self.text = text
        self.x = x
        self.y = y
        self.properties = kwargs # Store additional properties like color, font_size, etc.
        self.id = kwargs.pop('id', None) # Allow for ID for selection/manipulation

class FeynmanDiagramExtended(FeynmanDiagram):
    """
    Extends the FeynmanDiagram class to support:
    - Multiple Feynman diagrams within a single composite diagram.
    - Additional textual annotations.
    - Grouping of elements.
    - Enhanced selection and manipulation capabilities.
    - (Future) Layout management for sub-diagrams.
    """
    def __init__(self):
        super().__init__()
        self.sub_diagrams: List[FeynmanDiagram] = []
        self.text_elements: List[TextElement] = []
        self._text_element_ids = set() # To track unique IDs for text elements
        self.groups: Dict[str, List[str]] = {} # To store element IDs in groups
        self._next_group_id = 1 # For automatic group ID generation


    def _generate_unique_text_id(self):
        """Generates a unique ID for a text element."""
        i = 1
        while f"text_{i}" in self._text_element_ids:
            i += 1
        return f"text_{i}"

    def _generate_unique_group_id(self):
        """Generates a unique ID for a group."""
        group_id = f"group_{self._next_group_id}"
        while group_id in self.groups:
            self._next_group_id += 1
            group_id = f"group_{self._next_group_id}"
        return group_id

    # --- Management of Sub-Diagrams ---

    def add_sub_diagram(self, sub_diagram: FeynmanDiagram, position: Tuple[float, float] = (0.0, 0.0), sub_diagram_id: str = None) -> FeynmanDiagram:
        """
        Adds an existing FeynmanDiagram instance as a sub-diagram.
        The position specifies an offset for all elements within the sub-diagram relative to the main diagram's origin.

        Args:
            sub_diagram (FeynmanDiagram): The FeynmanDiagram instance to add.
            position (Tuple[float, float]): The (x, y) offset for this sub-diagram. Defaults to (0.0, 0.0).
            sub_diagram_id (str, optional): An optional unique ID for the sub-diagram. If None, a unique ID is generated.

        Returns:
            FeynmanDiagram: The added sub-diagram instance.

        Raises:
            TypeError: If sub_diagram is not an instance of FeynmanDiagram.
            ValueError: If the provided sub_diagram_id already exists.
        """
        if not isinstance(sub_diagram, FeynmanDiagram):
            raise TypeError("sub_diagram must be an instance of FeynmanDiagram.")

        if sub_diagram_id:
            if any(sd.id == sub_diagram_id for sd in self.sub_diagrams):
                raise ValueError(f"Sub-diagram ID '{sub_diagram_id}' already exists.")
            sub_diagram.id = sub_diagram_id # Assign ID to the sub-diagram itself for retrieval
        elif not hasattr(sub_diagram, 'id') or sub_diagram.id is None:
            # Generate a unique ID if the sub_diagram itself doesn't have one
            i = 1
            generated_id = f"subdiagram_{i}"
            while any(sd.id == generated_id for sd in self.sub_diagrams):
                i += 1
                generated_id = f"subdiagram_{i}"
            sub_diagram.id = generated_id

        # Store the position with the sub-diagram (e.g., as a custom attribute)
        # This approach assumes a rendering engine will use this 'offset' attribute.
        sub_diagram.offset = position
        self.sub_diagrams.append(sub_diagram)
        return sub_diagram

    def get_sub_diagram_by_id(self, sub_diagram_id: str) -> Optional[FeynmanDiagram]:
        """
        Retrieves a sub-diagram by its unique ID.

        Args:
            sub_diagram_id (str): The unique ID of the sub-diagram.

        Returns:
            Optional[FeynmanDiagram]: The FeynmanDiagram instance if found, otherwise None.
        """
        for sd in self.sub_diagrams:
            if hasattr(sd, 'id') and sd.id == sub_diagram_id:
                return sd
        return None

    def remove_sub_diagram(self, sub_diagram_id: str) -> bool:
        """
        Removes a sub-diagram from the composite diagram based on its ID.

        Args:
            sub_diagram_id (str): The ID of the sub-diagram to remove.

        Returns:
            bool: True if the sub-diagram was found and removed, False otherwise.
        """
        original_count = len(self.sub_diagrams)
        self.sub_diagrams = [sd for sd in self.sub_diagrams if not (hasattr(sd, 'id') and sd.id == sub_diagram_id)]
        return len(self.sub_diagrams) < original_count

    # --- Management of Additional Text ---

    def add_text(self, text: str, x: float, y: float, text_id: str = None, **kwargs) -> TextElement:
        """
        Adds a text annotation to the diagram.

        Args:
            text (str): The string content of the text.
            x (float): The X-coordinate for the text.
            y (float): The Y-coordinate for the text.
            text_id (str, optional): An optional unique ID for the text element. If None, a unique ID is generated.
            **kwargs: Additional properties for rendering the text (e.g., font_size, color, horizontalalignment).

        Returns:
            TextElement: The created TextElement instance.

        Raises:
            ValueError: If the provided text_id already exists.
        """
        if text_id:
            if text_id in self._text_element_ids:
                raise ValueError(f"Text ID '{text_id}' already exists. Please ensure all text IDs are unique.")
            final_id = text_id
        else:
            final_id = self._generate_unique_text_id()

        text_element = TextElement(text=text, x=x, y=y, id=final_id, **kwargs)
        self.text_elements.append(text_element)
        self._text_element_ids.add(final_id)
        return text_element

    def get_text_element_by_id(self, text_id: str) -> Optional[TextElement]:
        """
        Retrieves a text element by its unique ID.

        Args:
            text_id (str): The unique ID of the text element.

        Returns:
            Optional[TextElement]: The TextElement instance if found, otherwise None.
        """
        for text_el in self.text_elements:
            if text_el.id == text_id:
                return text_el
        return None

    def remove_text(self, text_id: str) -> bool:
        """
        Removes a text annotation from the diagram based on its ID.

        Args:
            text_id (str): The ID of the text element to remove.

        Returns:
            bool: True if the text element was found and removed, False otherwise.
        """
        original_count = len(self.text_elements)
        self.text_elements = [te for te in self.text_elements if te.id != text_id]
        if len(self.text_elements) < original_count:
            self._text_element_ids.discard(text_id)
            return True
        return False

    def update_text_element(self, text_id: str, new_text: str = None, new_x: float = None, new_y: float = None, **kwargs) -> bool:
        """
        Updates the properties of an existing text element.

        Args:
            text_id (str): The ID of the text element to update.
            new_text (str, optional): The new text content.
            new_x (float, optional): The new X-coordinate.
            new_y (float, optional): The new Y-coordinate.
            **kwargs: Any additional properties to update (e.g., color, font_size).

        Returns:
            bool: True if the text element was found and updated, False otherwise.
        """
        text_el = self.get_text_element_by_id(text_id)
        if text_el:
            if new_text is not None:
                text_el.text = new_text
            if new_x is not None:
                text_el.x = new_x
            if new_y is not None:
                text_el.y = new_y
            text_el.properties.update(kwargs)
            return True
        return False

    # --- Grouping of Elements ---

    def create_group(self, group_id: str = None, element_ids: Optional[List[str]] = None) -> str:
        """
        Creates a new group and optionally adds specified elements to it.

        Args:
            group_id (str, optional): A unique ID for the new group. If None, a unique ID is generated.
            element_ids (List[str], optional): A list of IDs of vertices, lines, or text elements to include in the group.

        Returns:
            str: The ID of the created group.

        Raises:
            ValueError: If the provided group_id already exists.
        """
        if group_id:
            if group_id in self.groups:
                raise ValueError(f"Group ID '{group_id}' already exists. Please choose a unique ID.")
            final_group_id = group_id
        else:
            final_group_id = self._generate_unique_group_id()

        self.groups[final_group_id] = []
        if element_ids:
            for element_id in element_ids:
                self.add_to_group(final_group_id, element_id)
        return final_group_id

    def add_to_group(self, group_id: str, element_id: str) -> bool:
        """
        Adds an element (vertex, line, or text) to an existing group.

        Args:
            group_id (str): The ID of the group to add to.
            element_id (str): The ID of the element to add.

        Returns:
            bool: True if the element was successfully added to the group, False otherwise.
                  Returns False if the group does not exist or the element does not exist.
        """
        if group_id not in self.groups:
            print(f"Warning: Group '{group_id}' does not exist.")
            return False

        # Check if the element actually exists in the diagram (either vertex, line, or text)
        if self.get_vertex_by_id(element_id) or \
           self.get_line_by_id(element_id) or \
           self.get_text_element_by_id(element_id):
            if element_id not in self.groups[group_id]:
                self.groups[group_id].append(element_id)
                return True
        else:
            print(f"Warning: Element with ID '{element_id}' not found in the diagram.")
        return False

    def remove_from_group(self, group_id: str, element_id: str) -> bool:
        """
        Removes an element from a specific group.

        Args:
            group_id (str): The ID of the group.
            element_id (str): The ID of the element to remove.

        Returns:
            bool: True if the element was successfully removed from the group, False otherwise.
        """
        if group_id in self.groups and element_id in self.groups[group_id]:
            self.groups[group_id].remove(element_id)
            return True
        return False

    def delete_group(self, group_id: str) -> bool:
        """
        Deletes a group. This does NOT delete the elements within the group.

        Args:
            group_id (str): The ID of the group to delete.

        Returns:
            bool: True if the group was found and deleted, False otherwise.
        """
        if group_id in self.groups:
            del self.groups[group_id]
            return True
        return False

    def get_group_elements(self, group_id: str) -> Optional[List[str]]:
        """
        Retrieves the IDs of all elements within a specific group.

        Args:
            group_id (str): The ID of the group.

        Returns:
            Optional[List[str]]: A list of element IDs if the group exists, otherwise None.
        """
        return self.groups.get(group_id)

    # --- Overridden and Extended Utility Methods ---

    def clear_diagram(self):
        """
        Clears all vertices, lines, sub-diagrams, text elements, and groups
        from the extended Feynman diagram.
        """
        super().clear_diagram() # Call the base class method to clear vertices and lines
        self.sub_diagrams.clear()
        self.text_elements.clear()
        self._text_element_ids.clear()
        self.groups.clear()
        self._next_group_id = 1

    def get_all_element_ids(self) -> List[str]:
        """
        Returns a list of all unique IDs for vertices, lines, and text elements
        in the main diagram. Does not include elements within sub-diagrams.
        """
        all_ids = list(self._vertex_ids) + list(self._line_ids) + list(self._text_element_ids)
        return all_ids

    def get_selected_item(self, selected_id: str, selected_type: str):
        """
        Extends the base method to also get selected sub-diagrams or text elements.

        Args:
            selected_id (str): The ID of the selected object.
            selected_type (str): The type of the selected object ('vertex', 'line', 'sub_diagram', 'text').

        Returns:
            Vertex, Line, FeynmanDiagram, TextElement: The instance if found, otherwise None.
        Raises:
            ValueError: If an unsupported selected_type is provided.
        """
        if selected_type == 'vertex' or selected_type == 'line':
            return super().get_selected_item(selected_id, selected_type)
        elif selected_type == 'sub_diagram':
            return self.get_sub_diagram_by_id(selected_id)
        elif selected_type == 'text':
            return self.get_text_element_by_id(selected_id)
        else:
            raise ValueError(f"Unsupported selected item type: '{selected_type}'.")

    # --- JSON Export/Import (Delegated to diagram_io) ---
    # These methods would be implemented in your diagram_io.py
    # They would need to handle the new structures (sub_diagrams, text_elements, groups)

    # def save(self, filename: str):
    #     from feynplot.io.diagram_io import export_diagram_to_json
    #     export_diagram_to_json(self, filename)

    # @classmethod
    # def load(cls, filename: str):
    #     from feynplot.io.diagram_io import import_diagram_from_json
    #     # This import function would need to return a new FeynmanDiagramExtended instance
    #     return import_diagram_from_json(filename, diagram_class=cls)