# feynplot_gui/controllers/toolbox_controller.py

import json
import os
from PySide6.QtCore import QObject, Signal
import numpy as np 
from collections import defaultdict

from feynplot_gui.core_ui.widgets.toolbox_widget import ToolboxWidget
from feynplot.io.diagram_io import diagram_to_json_string, diagram_from_json_string
from feynplot.core.diagram import FeynmanDiagram 


class ToolboxController(QObject):
    toggle_grid_visibility_requested = Signal() 
    
    def __init__(self, toolbox_widget: ToolboxWidget, main_controller: 'MainController', parent=None): 
        super().__init__(parent) 

        self.toolbox_widget = toolbox_widget
        self.main_controller = main_controller 
        
        self.undo_stack = []
        self.redo_stack = []
        self.max_history = 20

        self.setup_buttons()
        
        self._save_current_diagram_state()
        self._update_undo_redo_button_states()


    def setup_buttons(self):
        self.toolbox_widget.undo_action_requested.connect(self._on_undo_requested)
        self.toolbox_widget.redo_action_requested.connect(self._on_redo_requested)

        # self.toolbox_widget.add_vertex_requested.connect(self._on_add_vertex_requested)
        # self.toolbox_widget.add_line_requested.connect(self._on_add_line_requested)
        self.toolbox_widget.delete_vertex_requested.connect(self._on_delete_selected_vertex_requested)
        self.toolbox_widget.delete_line_requested.connect(self._on_delete_selected_line_requested)
        self.toolbox_widget.clear_diagram_requested.connect(self._on_clear_diagram_requested)

        self.toolbox_widget.request_auto_grid_adjustment.connect(self._on_auto_grid_adjustment_requested)
        
        self.toolbox_widget.show_all_vertices_requested.connect(self._on_show_all_vertices_requested)
        self.toolbox_widget.hide_all_vertices_requested.connect(self._on_hide_all_vertices_requested)

        self.toolbox_widget.show_all_vertex_labels_requested.connect(self._on_show_all_vertex_labels_requested)
        self.toolbox_widget.hide_all_vertex_labels_requested.connect(self._on_hide_all_vertex_labels_requested)

        self.toolbox_widget.show_all_line_labels_requested.connect(self._on_show_all_line_labels_requested)
        self.toolbox_widget.hide_all_line_labels_requested.connect(self._on_hide_all_line_labels_requested)

        self.toolbox_widget.request_auto_scale.connect(self._on_request_auto_scale)
        self.toolbox_widget.request_auto_set_line_angles.connect(self._on_request_auto_set_line_angles)
        self.toolbox_widget.request_toggle_grid_visibility.connect(self._on_request_toggle_grid_visibility)
        

    def _save_current_diagram_state(self,  message=None):
        """
        保存当前图的状态到撤销栈。
        """
        if message is None:
            current_state_json = diagram_to_json_string(self.main_controller.diagram_model)
        else:
            current_state_json = message
        self.undo_stack.append(current_state_json)
        # print(self._get_diagram_summary(self.main_controller.diagram_model))
        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)
        self.redo_stack.clear()
        self._update_undo_redo_button_states()
        # print(f"Saved state. Undo stack size: {len(self.undo_stack)}, Redo stack size: {len(self.redo_stack)}")


    def _restore_diagram_state(self, json_string: str):
        """
        从给定的 JSON 字符串恢复图的状态。
        """
        try:
            diagram_from_json_string(json_string, self.main_controller.diagram_model)
            self.main_controller.update_all_views()
            self._update_undo_redo_button_states()
            # print("图状态恢复成功。")
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            self.main_controller.status_message.emit(f"错误：恢复图状态失败：{e}")
            print(f"Error restoring diagram state: {e}")
            
            
    def _update_undo_redo_button_states(self):
        """
        根据撤销和重做栈的状态更新按钮的启用/禁用状态。
        """
        self.toolbox_widget.undo_button.setEnabled(len(self.undo_stack) > 1)
        self.toolbox_widget.redo_button.setEnabled(len(self.redo_stack) > 0)

    def _get_diagram_summary(self, diagram_model: FeynmanDiagram):
        """
        获取图模型的摘要信息（顶点和线条的数量及ID）。
        """
        vertex_ids = sorted([v.id for v in diagram_model.vertices])
        line_ids = sorted([l.id for l in diagram_model.lines])
        return {
            'vertex_count': len(vertex_ids),
            'vertex_ids': vertex_ids,
            'line_count': len(line_ids),
            'line_ids': line_ids
        }

    def _print_diagram_diff(self, old_summary, new_summary, operation_type: str):
        """
        打印两个图摘要之间的差异。
        """
        print(f"\n--- {operation_type} 操作引发的图对象变化 ---")
        
        # 顶点变化
        old_vertex_ids = set(old_summary['vertex_ids'])
        new_vertex_ids = set(new_summary['vertex_ids'])
        
        added_vertices = new_vertex_ids - old_vertex_ids
        removed_vertices = old_vertex_ids - new_vertex_ids
        
        if added_vertices:
            print(f"  新增顶点 (IDs): {', '.join(map(str, sorted(list(added_vertices))))}")
        if removed_vertices:
            print(f"  删除顶点 (IDs): {', '.join(map(str, sorted(list(removed_vertices))))}")
        if not added_vertices and not removed_vertices:
            print(f"  顶点数量不变 ({new_summary['vertex_count']})")
        
        # 线条变化
        old_line_ids = set(old_summary['line_ids'])
        new_line_ids = set(new_summary['line_ids'])
        
        added_lines = new_line_ids - old_line_ids
        removed_lines = old_line_ids - new_line_ids
        
        if added_lines:
            print(f"  新增线条 (IDs): {', '.join(map(str, sorted(list(added_lines))))}")
        if removed_lines:
            print(f"  删除线条 (IDs): {', '.join(map(str, sorted(list(removed_lines))))}")
        if not added_lines and not removed_lines:
            print(f"  线条数量不变 ({new_summary['line_count']})")
        
        if not added_vertices and not removed_vertices and not added_lines and not removed_lines:
            print("  图结构（顶点和线条）无明显增删变化。可能仅是属性变化或重新定位。")
            
        print("------------------------------------------")


    def _on_undo_requested(self):
        """
        处理撤销请求。
        """
        # print("Undo requested.") # 保持这个输出以指示操作开始
        if len(self.undo_stack) > 1:
            # 1. 记录恢复前的图状态摘要
            # pre_restore_summary = self._get_diagram_summary(self.main_controller.diagram_model)
            # self._save_current_diagram_state() # 保存当前状态到重做栈
            state_to_redo = self.undo_stack.pop() # 弹出当前状态
            self.redo_stack.append(state_to_redo) # 移到重做栈
            previous_state_json = self.undo_stack[-1] # 获取前一个状态 (将要恢复的状态)
            
            self._restore_diagram_state(previous_state_json)

            # 2. 记录恢复后的图状态摘要
            # post_restore_summary = self._get_diagram_summary(self.main_controller.diagram_model)
            
            # 3. 打印差异
            # print(f"撤销前栈大小: {len(self.undo_stack) + 1}, 重做前栈大小: {len(self.redo_stack) - 1}") # 打印操作前的实际大小
            # print(f"撤销后栈大小: {len(self.undo_stack)}, 重做后栈大小: {len(self.redo_stack)}")
            # self._print_diagram_diff(pre_restore_summary, post_restore_summary, "撤销")

            self.main_controller.status_message.emit("已撤销上一步操作。")
        else:
            self.main_controller.status_message.emit("没有更多可撤销的操作。")
            # print("没有更多可撤销的操作。") # 保持这个输出
        # print(f"Undo. Undo stack size: {len(self.undo_stack)}, Redo stack size: {len(self.redo_stack)}") # 最终状态输出


    def _on_redo_requested(self):
        """
        处理重做请求。
        """
        if self.redo_stack:
            # 1. 记录恢复前的图状态摘要
            pre_restore_summary = self._get_diagram_summary(self.main_controller.diagram_model)

            state_to_undo = self.redo_stack.pop() # 弹出要重做的状态
            self.undo_stack.append(state_to_undo) # 移到撤销栈
            
            self._restore_diagram_state(state_to_undo)

            # 2. 记录恢复后的图状态摘要
            # post_restore_summary = self._get_diagram_summary(self.main_controller.diagram_model)

            # # 3. 打印差异
            # print(f"重做前栈大小: {len(self.undo_stack) - 1}, 重做前栈大小: {len(self.redo_stack) + 1}") # 打印操作前的实际大小
            # print(f"重做后栈大小: {len(self.undo_stack)}, 重做后栈大小: {len(self.redo_stack)}")
            # self._print_diagram_diff(pre_restore_summary, post_restore_summary, "重做")
            
            self.main_controller.status_message.emit("已重做上一步操作。")
        else:
            self.main_controller.status_message.emit("没有更多可重做的操作。")

    def _on_delete_selected_vertex_requested(self):
        self.main_controller.delete_selected_object(object_type='vertex')
        self.main_controller.status_message.emit("已删除选定顶点。")
        self._save_current_diagram_state()
        self._update_undo_redo_button_states()

    def _on_delete_selected_line_requested(self):
        self.main_controller.delete_selected_object(object_type='line')
        self.main_controller.status_message.emit("已删除选定线条。")
        self._save_current_diagram_state()
        self._update_undo_redo_button_states()

    def _on_clear_diagram_requested(self):
        self.main_controller.clear_diagram()
        self.main_controller.status_message.emit("已清空图。")
        self._save_current_diagram_state()
        self._update_undo_redo_button_states()


    def _on_show_all_vertices_requested(self):
        self.main_controller.diagram_model.show_all_vertices()
        self.main_controller.status_message.emit("所有顶点已显示。")
        self.main_controller.update_all_views()
        self._save_current_diagram_state()
        self._update_undo_redo_button_states()

    def _on_hide_all_vertices_requested(self):
        self.main_controller.diagram_model.hide_all_vertices()
        self.main_controller.status_message.emit("所有顶点已隐藏。")
        self.main_controller.update_all_views()
        self._save_current_diagram_state()
        self._update_undo_redo_button_states()

    def _on_show_all_vertex_labels_requested(self):
        self.main_controller.diagram_model.show_all_vertice_labels()
        self.main_controller.status_message.emit("所有顶点标签已显示。")
        self.main_controller.update_all_views()
        self._save_current_diagram_state()
        self._update_undo_redo_button_states()

    def _on_hide_all_vertex_labels_requested(self):
        self.main_controller.diagram_model.hide_all_vertice_labels()
        self.main_controller.status_message.emit("所有顶点标签已隐藏。")
        self.main_controller.update_all_views()
        self._save_current_diagram_state()
        self._update_undo_redo_button_states()

    def _on_show_all_line_labels_requested(self):
        self.main_controller.diagram_model.show_all_line_labels()
        self.main_controller.status_message.emit("所有线标签已显示。")
        self.main_controller.update_all_views()
        self._save_current_diagram_state()
        self._update_undo_redo_button_states()

    def _on_hide_all_line_labels_requested(self):
        self.main_controller.diagram_model.hide_all_line_labels()
        self.main_controller.status_message.emit("所有线标签已隐藏。")
        self.main_controller.update_all_views()
        self._save_current_diagram_state()
        self._update_undo_redo_button_states()

    def _on_request_auto_scale(self):
        self.main_controller.status_message.emit("请求自动调整画布视图。")
        self.main_controller.update_all_views(canvas_options={'auto_scale': True})

    def _on_request_auto_set_line_angles(self):
        diagram_model = self.main_controller.diagram_model
        lines = diagram_model.lines

        vertex_pair_to_lines = defaultdict(list)
        self_loops = []

        for line in lines:
            if line.v_start == line.v_end:
                self_loops.append(line)
            else:
                vertex_key = frozenset({line.v_start.id, line.v_end.id})
                vertex_pair_to_lines[vertex_key].append(line)

        lines_processed = set()

        for vertex_key, connected_lines_group in vertex_pair_to_lines.items():
            num_parallel_lines = len(connected_lines_group)

            if num_parallel_lines < 2:
                continue

            for line in connected_lines_group:
                lines_processed.add(line)

            if num_parallel_lines == 2:
                line1, line2 = connected_lines_group
                line1.reset_angles(90)
                line2.reset_angles(-90)

            elif num_parallel_lines == 3:
                line_types_grouped = defaultdict(list)
                for line in connected_lines_group:
                    line_types_grouped[type(line)].append(line) 
                
                if len(line_types_grouped) == 1:
                    ordered_lines = list(connected_lines_group) 
                    ordered_lines[0].reset_angles(60)
                    ordered_lines[1].reset_angles(-60)
                    ordered_lines[2].reset_angles(0)
                    
                elif len(line_types_grouped) == 2:
                    odd_one_out_line = None
                    matching_lines = []

                    for line_type, lines_of_type in line_types_grouped.items():
                        if len(lines_of_type) == 1:
                            odd_one_out_line = lines_of_type[0]
                        else:
                            matching_lines.extend(lines_of_type)
                    
                    if odd_one_out_line:
                        odd_one_out_line.reset_angles(0)
                    
                    if len(matching_lines) == 2:
                        matching_lines[0].reset_angles(60)
                        matching_lines[1].reset_angles(-60)
                else:
                    for line in connected_lines_group:
                        line.reset_angles(0)
            
        for line in lines:
            if line in lines_processed:
                continue

            if line in self_loops:
                line.reset_angles(90)
            else:
                line.reset_angles(0)

        self.main_controller.status_message.emit("已自动设置所有线角度。")
        self.main_controller.update_all_views()
        self._save_current_diagram_state()
        self._update_undo_redo_button_states()
        return


    def _on_auto_grid_adjustment_requested(self):
        # print("执行自动调整格点操作...")

        if not self.main_controller.diagram_model:
            # print("错误：diagram_model 未初始化。")
            return

        vertices_to_update = self.main_controller.diagram_model.vertices

        if not vertices_to_update:
            # print("图中没有顶点可供调整。")
            return

        changes_made = False

        for vertex in vertices_to_update:
            original_x = vertex.x
            original_y = vertex.y

            new_x = int(np.round(original_x))
            new_y = int(np.round(original_y))

            if new_x != original_x or new_y != original_y:
                vertex.x = new_x
                vertex.y = new_y
                changes_made = True
                # print(f"顶点 {vertex.id} 从 ({original_x:.2f}, {original_y:.2f}) 调整到 ({new_x}, {new_y})")

        if changes_made:
            self.main_controller.update_all_views(canvas_options={'auto_scale': True})
            # print("自动调整格点完成，视图已更新。")
        else:
            # print("所有顶点已在格点上，无需调整。")
            pass
        self._save_current_diagram_state()
        self._update_undo_redo_button_states()


    def _on_request_toggle_grid_visibility(self):
        self.toggle_grid_visibility_requested.emit()
        # print(f"Grid visibility toggled. Current state: {self.main_controller.canvas_controller._canvas_instance.grid_on}")
        self.main_controller.status_message.emit(f"网格可见性已切换。")
        self.main_controller.update_all_views()


    def update_tool_mode(self, mode: str):
        if hasattr(self.toolbox_widget, 'add_vertex_button') and mode == 'add_vertex':
            self.toolbox_widget.add_vertex_button.setChecked(True)
        elif hasattr(self.toolbox_widget, 'add_line_button') and mode == 'add_line':
            self.toolbox_widget.add_line_button.setChecked(True)
        elif hasattr(self.toolbox_widget, 'selection_button') and mode == 'select':
            self.toolbox_widget.selection_button.setChecked(True)
        else:
            if hasattr(self.toolbox_widget, 'add_vertex_button'): self.toolbox_widget.add_vertex_button.setChecked(False)
            if hasattr(self.toolbox_widget, 'add_line_button'): self.toolbox_widget.add_line_button.setChecked(False)
            if hasattr(self.toolbox_widget, 'selection_button'): self.toolbox_widget.selection_button.setChecked(False)
            
        self.main_controller.status_message.emit(f"工具箱工具模式已更新为：{mode}")

    def update_redo_unto_status(self,message=None):
        self._save_current_diagram_state(message)
        self._update_undo_redo_button_states()
        self.main_controller.status_message.emit("撤销/重做状态已更新。")


    def update(self):
        pass