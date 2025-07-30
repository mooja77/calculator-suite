import os
import markdown

def get_content_blocks(block_ids):
    """Load content blocks from markdown files"""
    
    content_blocks = []
    content_dir = os.path.join(os.path.dirname(__file__), 'content')
    
    for block_id in block_ids:
        file_path = os.path.join(content_dir, f"{block_id}.md")
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse frontmatter and content
            lines = content.split('\n')
            title = block_id.replace('_', ' ').title()
            markdown_content = content
            
            # Look for title in first line if it starts with #
            if lines and lines[0].startswith('# '):
                title = lines[0][2:].strip()
                markdown_content = '\n'.join(lines[1:])
            
            # Convert markdown to HTML
            html_content = markdown.markdown(markdown_content)
            
            content_blocks.append({
                'id': block_id,
                'title': title,
                'content': html_content
            })
    
    return content_blocks