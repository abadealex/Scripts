
def export_marks_to_pdf(student_data, output_path):
    \"\"\"Generate a final marksheet PDF from student scores.\"\"\"
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Final Marksheet", ln=1, align='C')
    
    for student in student_data:
        line = f"{student['id']} - {student['name']} - {student['score']}"
        pdf.cell(200, 10, txt=line, ln=1, align='L')
    
    pdf.output(output_path)
    return output_path

