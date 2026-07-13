import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Merge Datasets", layout="wide")

st.title("دمج بيانات التأمين الصحي")

st.write("""
- ارفع الملف الأول (Source)
- ارفع الملف الثاني (Target)
- اختر الأعمدة التي تحتاج نقلها من الملف الأول إلى الملف الثاني
""")

# ==========================
# قراءة الملفات
# ==========================

source_file = st.file_uploader(
    " ارفع الملف الأول (Source)",
    type=["xlsx", "csv"],
    key="source"
)

target_file = st.file_uploader(
    " ارفع الملف الثاني (Target)",
    type=["xlsx", "csv"],
    key="target"
)


def read_file(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)


def clean_name(series):
    return (
        series.astype(str)
        .str.strip()
        .str.upper()
    )


if source_file and target_file:

    source_df = read_file(source_file)
    target_df = read_file(target_file)

    # ==========================
    # التأكد من وجود MEMBER NAME
    # ==========================

    if "MEMBER NAME" not in source_df.columns:
        st.error(" الملف الأول لا يحتوي على العمود MEMBER NAME")
        st.stop()

    if "MEMBER NAME" not in target_df.columns:
        st.error(" الملف الثاني لا يحتوي على العمود MEMBER NAME")
        st.stop()

    # تنظيف الأسماء
    source_df["MEMBER NAME"] = clean_name(source_df["MEMBER NAME"])
    target_df["MEMBER NAME"] = clean_name(target_df["MEMBER NAME"])

    # إزالة التكرارات
    source_df = source_df.drop_duplicates(subset="MEMBER NAME")

    # الأعمدة المتاحة
    available_columns = [
        c for c in source_df.columns
        if c != "MEMBER NAME"
    ]

    columns_to_copy = st.multiselect(
        "اختر الأعمدة التي تحتاج نقلها",
        available_columns
    )

    if columns_to_copy:

        lookup = source_df[["MEMBER NAME"] + columns_to_copy]

        result = target_df.merge(
            lookup,
            on="MEMBER NAME",
            how="left"
        )

        matched = result[columns_to_copy[0]].notna().sum()
        unmatched = len(result) - matched

        st.success(f"✅ تم ربط {matched} سجل")
        st.warning(f"⚠️ لم يتم العثور على {unmatched} سجل")

        st.subheader("معاينة البيانات")

        st.dataframe(result, use_container_width=True)

        output = BytesIO()

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            result.to_excel(writer, index=False, sheet_name="Merged")

        st.download_button(
            label="تحميل الملف النهائي",
            data=output.getvalue(),
            file_name="Merged_Dataset.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
