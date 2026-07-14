import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="دمج بيانات التأمين الصحي", layout="wide")
st.title("                ")

st.write("ارفع الملف الأول (Source) ثم الملف الثاني (Target).")

source_file = st.file_uploader("الملف الأول", type=["xlsx","csv"])
target_file = st.file_uploader("الملف الثاني", type=["xlsx","csv"])

def read_file(f):
    if f.name.lower().endswith(".csv"):
        return pd.read_csv(f)
    return pd.read_excel(f)

def clean_name(s):
    return s.astype(str).str.strip().str.upper()

if source_file and target_file:

    source_df = read_file(source_file)
    target_df = read_file(target_file)

    if "MEMBER NAME" not in source_df.columns:
        st.error("الملف الأول لا يحتوي على MEMBER NAME")
        st.stop()

    if "MEMBER NAME" not in target_df.columns:
        st.error("الملف الثاني لا يحتوي على MEMBER NAME")
        st.stop()

    source_df["MEMBER NAME"] = clean_name(source_df["MEMBER NAME"])
    target_df["MEMBER NAME"] = clean_name(target_df["MEMBER NAME"])

    source_df = source_df.drop_duplicates(subset="MEMBER NAME")

    available_columns = [
        c for c in source_df.columns
        if c != "MEMBER NAME"
    ]

    columns_to_copy = st.multiselect(
        "اختر الأعمدة المطلوب نقلها",
        available_columns
    )

    if columns_to_copy:

        lookup = source_df[["MEMBER NAME"] + columns_to_copy]

        merged = target_df.merge(
            lookup,
            on="MEMBER NAME",
            how="left"
        )

        missing = source_df[
            ~source_df["MEMBER NAME"].isin(target_df["MEMBER NAME"])
        ].copy()

        new_rows = pd.DataFrame(columns=merged.columns)

        for col in target_df.columns:
            if col in missing.columns:
                new_rows[col] = missing[col]
            else:
                new_rows[col] = None

        for col in columns_to_copy:
            new_rows[col] = missing[col]

        result = pd.concat([merged, new_rows], ignore_index=True)

        result = result.drop_duplicates(
            subset="MEMBER NAME",
            keep="first"
        )

        matched = result[result[columns_to_copy[0]].notna()].shape[0]

        st.success(f"تم إنشاء الملف النهائي بنجاح")
        st.info(f"عدد السجلات النهائية: {len(result)}")
        st.info(f"عدد السجلات المطابقة: {matched}")

        st.dataframe(result, use_container_width=True)

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            result.to_excel(writer, index=False, sheet_name="Merged")

        st.download_button(
            "تحميل الملف النهائي",
            data=output.getvalue(),
            file_name="Merged_Dataset.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
