import os
import datetime
from typing import Dict, Any

class ModelCardGenerator:
    @staticmethod
    def generate_model_card(model_name: str, 
                            version: str, 
                            config: Dict[str, Any], 
                            metrics: Dict[str, float], 
                            limitations: str) -> str:
        """
        Generates Model Card documentation in Markdown and HTML.
        Saves output files under backend/app/ml/model_cards/
        """
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 1. Build Markdown Content
        markdown = f"""# Model Card: {model_name}

## Model Information
* **Model Name:** {model_name}
* **Version:** {version}
* **Training Date:** {date_str}
* **Dataset Version:** dataset_v1

## Training Configuration
```yaml
"""
        for k, v in config.items():
            markdown += f"{k}: {v}\n"
            
        markdown += f"""```

## Evaluation Results
"""
        for metric, val in metrics.items():
            markdown += f"* **{metric}:** {val:.4f}\n"
            
        markdown += f"""
## Limitations & Considerations
{limitations}
"""
        
        # 2. Build HTML Content
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Model Card - {model_name}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; color: #333; }}
        h1 {{ color: #1a73e8; border-bottom: 2px solid #1a73e8; padding-bottom: 10px; }}
        h2 {{ color: #5f6368; margin-top: 30px; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 15px; }}
        th, td {{ border: 1px solid #dadce0; padding: 12px; text-align: left; }}
        th {{ background-color: #f8f9fa; }}
        pre {{ background-color: #f1f3f4; padding: 15px; border-radius: 4px; }}
    </style>
</head>
<body>
    <h1>Model Card: {model_name} (Version {version})</h1>
    <h2>Model Details</h2>
    <table>
        <tr><th>Key</th><th>Value</th></tr>
        <tr><td>Model Name</td><td>{model_name}</td></tr>
        <tr><td>Version</td><td>{version}</td></tr>
        <tr><td>Training Date</td><td>{date_str}</td></tr>
        <tr><td>Dataset Version</td><td>dataset_v1</td></tr>
    </table>
    
    <h2>Training Configuration</h2>
    <pre>"""
        for k, v in config.items():
            html += f"{k}: {v}\n"
            
        html += """</pre>
        
    <h2>Evaluation Results</h2>
    <table>
        <tr><th>Metric</th><th>Value</th></tr>"""
        for metric, val in metrics.items():
            html += f"<tr><td>{metric}</td><td>{val:.4f}</td></tr>"
            
        html += f"""
    </table>
    
    <h2>Limitations</h2>
    <p>{limitations}</p>
</body>
</html>
"""
        
        # Save files
        card_dir = os.path.dirname(os.path.abspath(__file__))
        md_path = os.path.join(card_dir, f"{model_name.lower().replace(' ', '_')}_card.md")
        html_path = os.path.join(card_dir, f"{model_name.lower().replace(' ', '_')}_card.html")
        
        try:
            with open(md_path, "w") as f:
                f.write(markdown)
            with open(html_path, "w") as f:
                f.write(html)
            print(f"[ModelCard] Generated card documentation for {model_name}: {md_path}")
        except Exception as e:
            print(f"Error generating model card: {e}")
            
        return md_path
