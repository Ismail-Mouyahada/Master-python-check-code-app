import streamlit as st
import subprocess
from radon.complexity import ComplexityVisitor
import ast
import os
import time

st.set_page_config(page_title="Comprehensive Code Analyzer", page_icon="📝", layout="wide")

# JavaScript for the page loader
loader_html = """
    <style>
    .loader-wrapper {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        display: none;
        align-items: center;
        justify-content: center;
        background-color: rgba(255, 255, 255, 0.7);
        z-index: 9999;
    }
    .loader {
        border: 12px solid #f3f3f3;
        border-radius: 50%;
        border-top: 12px solid #3498db;
        width: 60px;
        height: 60px;
        -webkit-animation: spin 1s linear infinite;
        animation: spin 1s linear infinite;
    }
    @-webkit-keyframes spin {
        0% { -webkit-transform: rotate(0deg); }
        100% { -webkit-transform: rotate(360deg); }
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
    <div class="loader-wrapper" id="loader-wrapper">
        <div class="loader"></div>
    </div>
    <script>
    function showLoader() {
        document.getElementById("loader-wrapper").style.display = "flex";
    }
    function hideLoader() {
        document.getElementById("loader-wrapper").style.display = "none";
    }
    </script>
"""

st.markdown(loader_html, unsafe_allow_html=True)

st.markdown("""
    <style>
        .stat-card {
            background-color: #2ecc71; /* Emerald */
            padding: 20px;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 20px;
        }
        .stat-card h3 {
            color: #ffffff;
        }
        .stat-card p {
            margin: 0;
        }
        .expander .streamlit-expanderHeader {
            background-color: #2ecc71;
            color: white;
            border-radius: 5px;
            padding: 10px;
        }
        .expander .streamlit-expanderContent {
            background-color: #ecfdf5;
            border: 1px solid #2ecc71;
            border-radius: 5px;
            padding: 10px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📝 Comprehensive Code Analyzer")
st.write("Upload your code files to analyze and get detailed insights on how to improve your code.")

# Checklist for code improvement
if st.button("Show Improvement Checklist"):
    with st.expander("Improvement Checklist"):
        st.checkbox("Ensure your code adheres to style guidelines to improve readability and maintainability.")
        st.checkbox("Reduce complexity to make your code more understandable and easier to maintain.")
        st.checkbox("Address security issues to ensure your code is secure and free from vulnerabilities.")
        st.checkbox("Add more comments to explain the purpose and functionality of your code.")
        st.checkbox("Optimize your code to improve performance.")
        st.checkbox("Keep your dependencies up to date to avoid vulnerabilities in third-party packages.")

uploaded_files = st.file_uploader("Choose Python files", type="py", accept_multiple_files=True)

code_files = {}
for uploaded_file in uploaded_files:
    code_files[uploaded_file.name] = uploaded_file.read().decode("utf-8")

# Function to check if executable exists
def check_executable(executable):
    return subprocess.run(['where' if os.name == 'nt' else 'which', executable], capture_output=True, text=True).returncode == 0

# Ensure flake8, bandit, and safety are installed and accessible
flake8_path = "flake8"
bandit_path = "bandit"
safety_path = "safety"

executables = {
    "flake8": flake8_path,
    "bandit": bandit_path,
    "safety": safety_path
}

missing_executables = [name for name, path in executables.items() if not check_executable(path)]

if missing_executables:
    st.error(f"One or more required executables ({', '.join(missing_executables)}) are not found. Please ensure they are installed and accessible in the system PATH. You can install them using `pip install {' '.join(missing_executables)}`.")
    st.stop()

def run_flake8(file_content, file_name):
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(file_content)
    result = subprocess.run([flake8_path, file_name], capture_output=True, text=True)
    os.remove(file_name)  # Clean up temporary file
    return result.stdout

def analyze_complexity(file_content):
    tree = ast.parse(file_content)
    complexity_visitor = ComplexityVisitor()
    complexity_visitor.visit(tree)
    return complexity_visitor.functions

def run_bandit(file_content, file_name):
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(file_content)
    result = subprocess.run([bandit_path, '-r', file_name], capture_output=True, text=True)
    os.remove(file_name)  # Clean up temporary file
    return result.stdout

def run_safety():
    result = subprocess.run([safety_path, 'check'], capture_output=True, text=True)
    return result.stdout

def analyze_comments(file_content):
    tree = ast.parse(file_content)
    comments = [node.value.s for node in ast.walk(tree) if isinstance(node, ast.Expr) and isinstance(node.value, ast.Str)]
    return comments

def performance_analysis(file_content):
    try:
        start_time = time.time()
        exec(file_content)
        exec_time = time.time() - start_time
        return f"Execution time: {exec_time:.4f} seconds"
    except Exception as e:
        return f"Error during execution: {str(e)}"

def display_card(title, content, advice=None):
    with st.expander(title, expanded=True):
        st.code(content, language='plaintext')
        if advice:
            st.warning(advice)

def display_stat_card(title, value, description):
    st.markdown(
        f"""
        <div class="stat-card">
            <h3>{title}</h3>
            <p style="font-size: 24px; font-weight: bold;">{value}</p>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if code_files:
    st.markdown('<script>showLoader();</script>', unsafe_allow_html=True)
    with st.spinner("Analyzing files..."):
        for file_name, file_content in code_files.items():
            st.subheader(f"Results for {file_name}")

            # Displaying statistics at the top
            col1, col2 = st.columns(2)
            total_lines = len(file_content.splitlines())
            total_comments = len(analyze_comments(file_content))
            total_complexity = len(analyze_complexity(file_content))
            total_security_issues = len(run_bandit(file_content, file_name).splitlines())

            with col1:
                display_stat_card("Total Lines of Code", total_lines, "The total number of lines in the file.")
                display_stat_card("Total Comments", total_comments, "The number of comment lines in the file.")

            with col2:
                display_stat_card("Complex Functions", total_complexity, "The number of functions with high complexity.")
                display_stat_card("Security Issues", total_security_issues, "The number of security issues found.")

            col1, col2 = st.columns(2)
            with col1:
                st.write("### Syntax and Style Analysis")
                flake8_output = run_flake8(file_content, file_name)
                flake8_advice = "Ensure your code adheres to style guidelines to improve readability and maintainability."
                display_card("Flake8 Results", flake8_output, flake8_advice)

                st.write("### Complexity Analysis")
                complexity_results = analyze_complexity(file_content)
                complexity_content = "\n".join(str(result) for result in complexity_results)
                complexity_advice = "Reduce complexity to make your code more understandable and easier to maintain."
                display_card("Complexity Results", complexity_content, complexity_advice)
            with col2:
                st.write("### Security Analysis")
                bandit_output = run_bandit(file_content, file_name)
                bandit_advice = "Address security issues to ensure your code is secure and free from vulnerabilities."
                display_card("Security Results", bandit_output, bandit_advice)

                st.write("### Comment Analysis")
                comments = analyze_comments(file_content)
                comments_content = "\n".join(comments)
                comments_advice = "Add more comments to explain the purpose and functionality of your code."
                display_card("Comments Analysis", comments_content, comments_advice)

                st.write("### Performance Analysis")
                performance_output = performance_analysis(file_content)
                performance_advice = "Optimize your code to improve performance."
                display_card("Performance Analysis", performance_output, performance_advice)
    st.markdown('<script>hideLoader();</script>', unsafe_allow_html=True)

if st.button("Check Dependencies"):
    st.markdown('<script>showLoader();</script>', unsafe_allow_html=True)
    with st.spinner("Checking dependencies..."):
        st.subheader("Dependency Analysis")
        safety_output = run_safety()
        safety_advice = "Keep your dependencies up to date to avoid vulnerabilities in third-party packages."
        display_card("Dependency Analysis", safety_output, safety_advice)
    st.markdown('<script>hideLoader();</script>', unsafe_allow_html=True)
