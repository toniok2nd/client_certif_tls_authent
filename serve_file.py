import argparse
import gradio as gr
import os

# Define the argument parser
parser = argparse.ArgumentParser(description='TLS-enabled file server with password protection using Gradio')
parser.add_argument('--cert', default='server/server.crt', help='Path to the SSL certificate file')
parser.add_argument('--key', default='server/server.key', help='Path to the SSL key file')
parser.add_argument('--password', required=True, help='Password to protect the file download')
parser.add_argument('--file', required=True, help='Full path to the file to serve')

args = parser.parse_args()

# Function to check the password
def check_password(password):
    return password == args.password

# Function to serve the file
def download_file(password):
    if not check_password(password):
        return "Invalid password"
    file_path = args.file
    if not os.path.exists(file_path):
        return "File not found"
    return file_path

# Create the Gradio interface
iface = gr.Interface(
    fn=download_file,
    inputs=gr.Textbox(label="Password"),
    outputs=gr.File(label="Download File"),
    title="Secure File Download",
    description="Enter the password to download the file."
)

# Launch the Gradio interface with SSL context
iface.launch(server_name="0.0.0.0", server_port=7860, ssl_keyfile=args.key, ssl_certfile=args.cert, ssl_verify=False)

