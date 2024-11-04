import pandas as pd
from .generate_code import generate_code_process_data
class ProcessData:
    def __init__(self, df):
        self.df = df

    @classmethod
    def load_data(cls, file_path):
        """
        Load dữ liệu từ file_path và trả về một instance của ProcessData.
        """
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        return cls(df)

    def process_data_df(self, metadata):
        """
        Thực hiện các bước xử lý dữ liệu trên DataFrame và trả về DataFrame đã xử lý.
        """
        # Gọi hàm generate_code_process_data để sinh mã code dựa trên metadata
        code = generate_code_process_data(metadata)
        print("Using:")
        print(code)
        # Thực thi mã code được sinh ra
        # Lưu code dưới dạng hàm 'process' trong ngữ cảnh cục bộ
        local_context = {}
        exec(code, {}, local_context)

        # Gọi hàm process trên DataFrame
        if 'process' in local_context:
            self.df = local_context['process'](self.df)

        return self.df
    def get_summary_data(self):
        """
        Tạo một bản tóm tắt dữ liệu dưới dạng HTML.
        """
        return self.df.describe().to_html(classes='table table-striped')
