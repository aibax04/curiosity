from pathlib import Path

# Complete frontend HTML with FIXED error handling
frontend_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Web App Generator</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🤖</text></svg>">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            overflow: hidden;
        }

        .container {
            width: 100%;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }

        .prompt-section {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
            transition: all 0.6s ease;
        }

        .prompt-section.minimized {
            flex: 0 0 80px;
            padding: 1rem 2rem;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }

        .prompt-wrapper {
            max-width: 700px;
            width: 100%;
        }

        .prompt-section.minimized .prompt-wrapper {
            max-width: 100%;
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        h1 {
            color: white;
            font-size: 3rem;
            margin-bottom: 1rem;
            text-align: center;
            text-shadow: 0 2px 20px rgba(0, 0, 0, 0.2);
        }

        .prompt-section.minimized h1 {
            font-size: 1.5rem;
            margin-bottom: 0;
            text-align: left;
        }

        .subtitle {
            color: rgba(255, 255, 255, 0.9);
            font-size: 1.2rem;
            text-align: center;
            margin-bottom: 3rem;
        }

        .prompt-section.minimized .subtitle {
            display: none;
        }

        .input-container {
            position: relative;
            width: 100%;
        }

        .prompt-section.minimized .input-container {
            flex: 1;
        }

        .prompt-input {
            width: 100%;
            padding: 1.5rem 5rem 1.5rem 1.5rem;
            font-size: 1.1rem;
            border: none;
            border-radius: 50px;
            background: white;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            outline: none;
        }

        .prompt-section.minimized .prompt-input {
            padding: 0.8rem 4rem 0.8rem 1.2rem;
            font-size: 1rem;
            border-radius: 30px;
        }

        .generate-btn {
            position: absolute;
            right: 8px;
            top: 50%;
            transform: translateY(-50%);
            padding: 0.8rem 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 40px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            transition: transform 0.2s ease;
        }

        .generate-btn:hover:not(:disabled) {
            transform: translateY(-50%) scale(1.05);
        }

        .generate-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        .loading {
            display: none;
            text-align: center;
            color: white;
            margin-top: 2rem;
        }

        .loading.active {
            display: block;
        }

        .spinner {
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-top: 3px solid white;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .split-view {
            flex: 1;
            display: none;
            opacity: 0;
        }

        .split-view.active {
            display: flex;
            animation: fadeIn 0.6s ease forwards;
        }

        @keyframes fadeIn {
            to { opacity: 1; }
        }

        .panel {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: white;
            margin: 1rem;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            overflow: hidden;
        }

        .panel-header {
            padding: 1rem 1.5rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: 600;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .panel-tools {
            display: flex;
            gap: 0.5rem;
        }

        .tool-btn {
            background: rgba(255, 255, 255, 0.2);
            border: none;
            color: white;
            padding: 0.4rem 0.8rem;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9rem;
            transition: background 0.2s ease;
        }

        .tool-btn:hover {
            background: rgba(255, 255, 255, 0.3);
        }

        .panel-content {
            flex: 1;
            overflow: auto;
        }

        .code-editor {
            width: 100%;
            height: 100%;
            padding: 1.5rem;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.6;
            border: none;
            outline: none;
            resize: none;
            background: #1e1e1e;
            color: #d4d4d4;
        }

        .preview-frame {
            width: 100%;
            height: 100%;
            border: none;
            background: white;
        }

        .file-tabs {
            display: flex;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            background: #f5f5f5;
            border-bottom: 1px solid #ddd;
            overflow-x: auto;
        }

        .file-tab {
            padding: 0.5rem 1rem;
            background: white;
            border: 1px solid #ddd;
            border-radius: 6px 6px 0 0;
            cursor: pointer;
            font-size: 0.9rem;
            white-space: nowrap;
            transition: background 0.2s ease;
        }

        .file-tab:hover {
            background: #f9f9f9;
        }

        .file-tab.active {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }

        .status-bar {
            padding: 0.5rem 1rem;
            background: #f5f5f5;
            border-top: 1px solid #ddd;
            font-size: 0.85rem;
            color: #666;
            display: flex;
            justify-content: space-between;
        }

        .error-message {
            background: #fee;
            border: 1px solid #fcc;
            color: #c00;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 8px;
            display: none;
            white-space: pre-wrap;
            font-size: 0.9rem;
        }

        .error-message.active {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="prompt-section" id="promptSection">
            <div class="prompt-wrapper">
                <h1>AI Web App Generator</h1>
                <p class="subtitle">Describe your app and watch it come to life</p>
                
                <div class="input-container">
                    <input 
                        type="text" 
                        class="prompt-input" 
                        id="promptInput"
                        placeholder="e.g., Build a colorful modern todo app"
                    >
                    <button class="generate-btn" id="generateBtn">Generate</button>
                </div>

                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>Generating your app...</p>
                </div>

                <div class="error-message" id="errorMessage"></div>
            </div>
        </div>

        <div class="split-view" id="splitView">
            <div class="panel">
                <div class="panel-header">
                    <span>Code Editor</span>
                    <div class="panel-tools">
                        <button class="tool-btn" id="copyBtn">Copy</button>
                        <button class="tool-btn" id="downloadBtn">Download</button>
                    </div>
                </div>
                <div class="file-tabs" id="fileTabs"></div>
                <div class="panel-content">
                    <textarea class="code-editor" id="codeEditor" spellcheck="false"></textarea>
                </div>
                <div class="status-bar">
                    <span id="fileInfo">No file selected</span>
                    <span id="lineInfo">Lines: 0</span>
                </div>
            </div>

            <div class="panel">
                <div class="panel-header">
                    <span>Live Preview</span>
                    <div class="panel-tools">
                        <button class="tool-btn" id="refreshBtn">Refresh</button>
                    </div>
                </div>
                <div class="panel-content">
                    <iframe class="preview-frame" id="previewFrame"></iframe>
                </div>
            </div>
        </div>
    </div>

    <script>
        const state = { files: {}, currentFile: null };
        
        const promptSection = document.getElementById('promptSection');
        const promptInput = document.getElementById('promptInput');
        const generateBtn = document.getElementById('generateBtn');
        const loading = document.getElementById('loading');
        const splitView = document.getElementById('splitView');
        const codeEditor = document.getElementById('codeEditor');
        const previewFrame = document.getElementById('previewFrame');
        const fileTabs = document.getElementById('fileTabs');
        const fileInfo = document.getElementById('fileInfo');
        const lineInfo = document.getElementById('lineInfo');
        const errorMessage = document.getElementById('errorMessage');

        // Event listeners
        generateBtn.addEventListener('click', handleGenerate);
        promptInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') handleGenerate();
        });
        codeEditor.addEventListener('input', handleCodeChange);
        document.getElementById('copyBtn').addEventListener('click', copyCode);
        document.getElementById('downloadBtn').addEventListener('click', downloadCode);
        document.getElementById('refreshBtn').addEventListener('click', updatePreview);

        function showError(message) {
            errorMessage.textContent = message;
            errorMessage.classList.add('active');
            setTimeout(() => {
                errorMessage.classList.remove('active');
            }, 8000);
        }

        async function handleGenerate() {
            const prompt = promptInput.value.trim();
            if (!prompt) {
                showError('Please enter a prompt');
                return;
            }

            generateBtn.disabled = true;
            loading.classList.add('active');
            errorMessage.classList.remove('active');

            try {
                console.log('Sending request to backend...');
                const response = await fetch('http://localhost:8000/api/generate', {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify({ user_prompt: prompt })
                });

                console.log('Response status:', response.status);

                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error('Backend error (' + response.status + '): ' + errorText);
                }

                const data = await response.json();
                console.log('Received data:', data);
                
                if (data.files && Object.keys(data.files).length > 0) {
                    state.files = data.files;
                    renderFileTabs();
                    const firstFile = Object.keys(state.files)[0];
                    selectFile(firstFile);
                    
                    loading.classList.remove('active');
                    promptSection.classList.add('minimized');
                    splitView.classList.add('active');
                } else {
                    showError('No files were generated. Please try again with a different prompt.');
                }
            } catch (error) {
                console.error('Generation error:', error);
                showError(error.message + '\\n\\nMake sure the backend is running on http://localhost:8000');
            } finally {
                loading.classList.remove('active');
                generateBtn.disabled = false;
            }
        }

        function renderFileTabs() {
            fileTabs.innerHTML = '';
            Object.keys(state.files).forEach(filename => {
                const tab = document.createElement('div');
                tab.className = 'file-tab';
                tab.textContent = filename;
                tab.addEventListener('click', () => selectFile(filename));
                fileTabs.appendChild(tab);
            });
        }

        function selectFile(filename) {
            state.currentFile = filename;
            codeEditor.value = state.files[filename] || '';
            
            document.querySelectorAll('.file-tab').forEach(tab => {
                tab.classList.toggle('active', tab.textContent === filename);
            });

            updateFileInfo();
            updatePreview();
        }

        function handleCodeChange() {
            if (state.currentFile) {
                state.files[state.currentFile] = codeEditor.value;
                updateFileInfo();
                updatePreview();
            }
        }

        function updateFileInfo() {
            if (state.currentFile) {
                const lines = codeEditor.value.split('\\n').length;
                fileInfo.textContent = state.currentFile;
                lineInfo.textContent = 'Lines: ' + lines;
            }
        }

        function updatePreview() {
            const htmlFile = Object.keys(state.files).find(f => f.endsWith('.html'));
            if (!htmlFile) return;

            let html = state.files[htmlFile];
            const cssFile = Object.keys(state.files).find(f => f.endsWith('.css'));
            const jsFile = Object.keys(state.files).find(f => f.endsWith('.js'));

            if (cssFile && state.files[cssFile]) {
                html = html.replace('</head>', '<style>' + state.files[cssFile] + '</style></head>');
            }
            if (jsFile && state.files[jsFile]) {
                html = html.replace('</body>', '<script>' + state.files[jsFile] + '<\\/script></body>');
            }

            const blob = new Blob([html], { type: 'text/html' });
            previewFrame.src = URL.createObjectURL(blob);
        }

        function copyCode() {
            if (!state.currentFile) {
                showError('No file selected');
                return;
            }
            navigator.clipboard.writeText(codeEditor.value).then(() => {
                const btn = document.getElementById('copyBtn');
                const originalText = btn.textContent;
                btn.textContent = 'Copied!';
                setTimeout(() => btn.textContent = originalText, 2000);
            }).catch(() => {
                codeEditor.select();
                document.execCommand('copy');
                alert('Code copied!');
            });
        }

        function downloadCode() {
            if (!state.currentFile) {
                showError('No file selected');
                return;
            }
            const blob = new Blob([codeEditor.value], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = state.currentFile;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }

        console.log('✅ Frontend loaded successfully');
        console.log('📡 Backend API: http://localhost:8000');
        console.log('🎨 Ready to generate apps!');
    </script>
</body>
</html>
"""

def main():
    """Create frontend directory and save index.html"""
    script_dir = Path(__file__).parent
    frontend_dir = script_dir / "frontend"
    frontend_dir.mkdir(exist_ok=True)
    
    index_path = frontend_dir / "index.html"
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(frontend_html)
    
    print("="*60)
    print("✅ Frontend setup complete!")
    print("="*60)
    print(f"📁 Created: {index_path}")
    print(f"📏 Size: {len(frontend_html)} bytes")
    print("\n🚀 Next steps:")
    print("   1. Run: python dev.py")
    print("   2. Open: http://localhost:3000")
    print("   3. Start building apps!")
    print("="*60)

if __name__ == "__main__":
    main()