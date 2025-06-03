import streamlit as st
import base64
import io
import matplotlib.pyplot as plt

def get_image_download_link(fig, filename, text):
    """Generate a link to download a figure as PNG"""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    return f'<a href="data:image/png;base64,{b64}" download="{filename}.png">{text}</a>'

def get_copy_button_html(element_id, button_text="Copy to Clipboard"):
    """Generate HTML/JS for a copy to clipboard button"""
    return f"""
    <button id="{element_id}_btn" class="copy-btn" 
        onclick="copyCanvas('{element_id}')">
        {button_text}
    </button>
    <script>
    function copyCanvas(elementId) {{
        const canvas = document.getElementById(elementId).querySelector('canvas');
        if (!canvas) {{
            console.error('Canvas not found');
            return;
        }}
        
        // Create temporary canvas to handle transparent background
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = canvas.width;
        tempCanvas.height = canvas.height;
        
        const ctx = tempCanvas.getContext('2d');
        // Fill with white background
        ctx.fillStyle = '#FFFFFF';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Draw the original canvas on top
        ctx.drawImage(canvas, 0, 0);
        
        tempCanvas.toBlob(function(blob) {{
            const item = new ClipboardItem({{'image/png': blob}});
            navigator.clipboard.write([item]).then(
                function() {{
                    const btn = document.getElementById(elementId + '_btn');
                    const originalText = btn.innerText;
                    btn.innerText = 'Copied!';
                    setTimeout(function() {{
                        btn.innerText = originalText;
                    }}, 2000);
                }}
            );
        }});
    }}
    </script>
    """

def add_copy_button_to_figure(fig_html, element_id):
    """Add a copy button beneath a streamlit figure"""
    # Don't try to convert or manipulate the fig_html - just use it as a reference
    copy_button = get_copy_button_html(element_id)
    return f"""
    <div id="{element_id}">
        <!-- Figure placeholder - will be filled by Streamlit -->
    </div>
    {copy_button}
    """

def copy_all_button(element_ids):
    """Create a button to copy all charts to clipboard"""
    ids_str = "','".join(element_ids)
    return f"""
    <button class="copy-btn" style="margin-bottom: 20px; background-color: #059669;"
        onclick="copyAllCanvases(['{ids_str}'])">
        Copy All Charts to Clipboard
    </button>
    <script>
    async function copyAllCanvases(elementIds) {{
        // Create a new canvas to hold all charts
        const masterCanvas = document.createElement('canvas');
        let totalHeight = 0;
        let maxWidth = 0;
        const padding = 20;
        
        // First pass: calculate dimensions
        for (const id of elementIds) {{
            const canvas = document.getElementById(id).querySelector('canvas');
            if (canvas) {{
                totalHeight += canvas.height + padding;
                maxWidth = Math.max(maxWidth, canvas.width);
            }}
        }}
        
        // Set master canvas dimensions
        masterCanvas.width = maxWidth;
        masterCanvas.height = totalHeight;
        
        // Get context and fill with white background
        const ctx = masterCanvas.getContext('2d');
        ctx.fillStyle = '#FFFFFF';
        ctx.fillRect(0, 0, masterCanvas.width, masterCanvas.height);
        
        // Second pass: draw each canvas
        let currentY = 0;
        for (const id of elementIds) {{
            const canvas = document.getElementById(id).querySelector('canvas');
            if (canvas) {{
                // Center the image horizontally
                const x = (maxWidth - canvas.width) / 2;
                ctx.drawImage(canvas, x, currentY);
                currentY += canvas.height + padding;
            }}
        }}
        
        // Copy to clipboard
        masterCanvas.toBlob(function(blob) {{
            const item = new ClipboardItem({{'image/png': blob}});
            navigator.clipboard.write([item]).then(
                function() {{
                    // Show success message
                    const btn = document.querySelector('button[onclick*="copyAllCanvases"]');
                    const originalText = btn.innerText;
                    btn.innerText = 'All Charts Copied!';
                    setTimeout(function() {{
                        btn.innerText = originalText;
                    }}, 2000);
                }}
            );
        }});
    }}
    </script>
    """