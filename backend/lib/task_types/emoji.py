from emoji import demojize, replace_emoji
import pyarrow
from pipeline.task import OneToOneRowwiseTask

# class RemoveEmoji(OneToOneRowwiseTask):
#     def execute(self, *text):
#         return tuple(t.as_py().casefold() for t in text)


#         mode = streamlit.selectbox("What do you want to replace the emoji with?", self._MODES)
#         replace_with = None

#         if mode == self._MODES[1]:
#             replace_with = streamlit.text_input("What string do you want to replace the emoji with?")
#         elif mode == self._MODES[2]:
#             replace_with = ""

#         return {"replace_with": replace_with}

#     def execute(self, *text):
#         result = []
#         for t in text:
#             t = t.as_py()

#         replace_with = self.config.get("replace_with")
#         if isinstance(replace_with, str):
#             return replace_emoji(text, replace_with)
#         return demojize(text)

#     def schema(self):
#         column_names = self.column.value
#         if not isinstance(self.column.value, list):
#             column_names = [column_names]

#         return pyarrow.schema(
#             {name + "_demojized": pyarrow.string() for name in column_names}
#         )
