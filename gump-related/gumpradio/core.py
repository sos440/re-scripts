from AutoComplete import *
from typing import List, Optional, Tuple, Union


# with gr.Blocks() as demo:
#     gr.Markdown("## 🖼️ LLM 인터페이스")

#     with gr.Row():
#         with gr.Column():
#             prompt_input = gr.Textbox(
#                 lines=3, placeholder="여기에 프롬프트를 입력하세요...", label="프롬프트"
#             )
#             submit_btn = gr.Button("생성하기", variant="primary")
#             image_input = gr.Image(type="pil", label="이미지 업로드")

#         with gr.Column():
#             with gr.Group(visible=True):
#                 gr.Markdown("### ✨ 결과물")
#                 text_output = gr.Textbox(label="결과 텍스트")
#                 image_output = gr.Image(label="결과 이미지")

#     # 버튼 클릭 이벤트와 함수 연결
#     submit_btn.click(
#         fn=your_llm_function,
#         inputs=[prompt_input, image_input],
#         outputs=[text_output, image_output, image_output],
#     )

# demo.launch()


class Block:
    def __init__(self):
        self.parent: Optional["Block"] = None
        self.has_children: bool = False


class Container(Block):
    def __init__(self):
        super().__init__()
        self.has_children = True
        self.children: List["Block"] = []


class Row(Container): ...


class Column(Container): ...


class GumpBuilder:
    class Scope:
        def __init__(self, builder: "GumpBuilder", block: Container):
            self.builder = builder
            self.block = block

        def __enter__(self):
            cur_block = self.builder.current
            assert isinstance(cur_block, Container), "Current block must be a container."
            cur_block.children.append(self.block)
            self.block.parent = cur_block
            self.builder.current = self.block
            return self.block

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.builder.current = self.block.parent if self.block.parent else self.builder.root

    def __init__(self):
        self.root: Block = Row()
        self.current: Block = self.root

    def Row(self):
        return self.Scope(self, Row())

    def Column(self):
        return self.Scope(self, Column())
