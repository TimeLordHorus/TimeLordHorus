// Code Runner VM - Execute code in sandboxed environment
class CodeRunner {
    constructor() {
        this.snippets = [];
        this.pyodideLoaded = false;
        this.pyodide = null;

        this.init();
    }

    async init() {
        await this.loadSnippets();
        this.setupEventListeners();
        this.setupConsoleInterception();
    }

    setupEventListeners() {
        // Open code runner
        document.getElementById('codeRunnerBtn').addEventListener('click', () => {
            this.openCodeRunner();
        });

        // Close code runner
        document.getElementById('closeCodeRunner').addEventListener('click', () => {
            this.closeCodeRunner();
        });

        // Click outside to close
        document.getElementById('codeRunnerPanel').addEventListener('click', (e) => {
            if (e.target.id === 'codeRunnerPanel') {
                this.closeCodeRunner();
            }
        });

        // Run code
        document.getElementById('runCodeBtn').addEventListener('click', () => {
            this.runCode();
        });

        // Clear code
        document.getElementById('clearCodeBtn').addEventListener('click', () => {
            document.getElementById('codeEditor').value = '';
        });

        // Save code
        document.getElementById('saveCodeBtn').addEventListener('click', () => {
            this.saveSnippet();
        });

        // Load code
        document.getElementById('loadCodeBtn').addEventListener('click', () => {
            this.loadSnippet();
        });

        // Import code
        document.getElementById('importCodeBtn').addEventListener('click', () => {
            this.importCode();
        });

        // Clear console
        document.getElementById('clearConsoleBtn').addEventListener('click', () => {
            this.clearConsole();
        });

        // Clear snippets
        document.getElementById('clearSnippetsBtn').addEventListener('click', () => {
            this.clearAllSnippets();
        });

        // Language change
        document.getElementById('languageSelect').addEventListener('change', () => {
            this.updateEditorPlaceholder();
        });
    }

    setupConsoleInterception() {
        // Create custom console for capturing output
        this.originalConsole = {
            log: console.log,
            error: console.error,
            warn: console.warn,
            info: console.info
        };
    }

    openCodeRunner() {
        document.getElementById('codeRunnerPanel').classList.add('open');
    }

    closeCodeRunner() {
        document.getElementById('codeRunnerPanel').classList.remove('open');
    }

    updateEditorPlaceholder() {
        const language = document.getElementById('languageSelect').value;
        const editor = document.getElementById('codeEditor');
        const placeholders = {
            javascript: '// Write your JavaScript code here\nconsole.log("Hello from TimeLord Browser VM!");',
            html: '<!-- Write your HTML/CSS code here -->\n<!DOCTYPE html>\n<html>\n<head>\n    <style>\n        body { font-family: Arial; padding: 20px; }\n    </style>\n</head>\n<body>\n    <h1>Hello World!</h1>\n</body>\n</html>',
            python: '# Write your Python code here\nprint("Hello from Python!")',
            typescript: '// Write your TypeScript code here\nconst greeting: string = "Hello from TypeScript!";\nconsole.log(greeting);'
        };

        if (!editor.value || editor.value === placeholders[language]) {
            editor.value = placeholders[language];
        }
    }

    async runCode() {
        const code = document.getElementById('codeEditor').value;
        const language = document.getElementById('languageSelect').value;

        this.clearConsole();
        this.log('info', `Executing ${language} code...`);

        try {
            switch (language) {
                case 'javascript':
                    await this.runJavaScript(code);
                    break;
                case 'html':
                    await this.runHTML(code);
                    break;
                case 'python':
                    await this.runPython(code);
                    break;
                case 'typescript':
                    await this.runTypeScript(code);
                    break;
            }
        } catch (error) {
            this.log('error', `Error: ${error.message}`);
            console.error(error);
        }
    }

    async runJavaScript(code) {
        // Create a sandboxed iframe for code execution
        const iframe = document.createElement('iframe');
        iframe.style.display = 'none';
        iframe.sandbox = 'allow-scripts';
        document.body.appendChild(iframe);

        // Inject custom console
        const iframeWindow = iframe.contentWindow;
        const codeRunner = this;

        iframeWindow.console = {
            log: (...args) => codeRunner.log('success', args.join(' ')),
            error: (...args) => codeRunner.log('error', args.join(' ')),
            warn: (...args) => codeRunner.log('warn', args.join(' ')),
            info: (...args) => codeRunner.log('info', args.join(' '))
        };

        try {
            // Execute code in iframe
            iframeWindow.eval(code);
            this.log('info', 'Execution completed successfully');
        } catch (error) {
            this.log('error', `Runtime Error: ${error.message}`);
        } finally {
            setTimeout(() => document.body.removeChild(iframe), 100);
        }
    }

    async runHTML(code) {
        // Create a new window/tab for HTML preview
        const previewWindow = window.open('', '_blank');

        if (!previewWindow) {
            this.log('error', 'Please allow popups for HTML preview');
            return;
        }

        previewWindow.document.open();
        previewWindow.document.write(code);
        previewWindow.document.close();

        this.log('success', 'HTML preview opened in new tab');
    }

    async runPython(code) {
        this.log('info', 'Loading Python interpreter (Pyodide)...');

        if (!this.pyodideLoaded) {
            try {
                // Load Pyodide from CDN
                const script = document.createElement('script');
                script.src = 'https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js';

                await new Promise((resolve, reject) => {
                    script.onload = resolve;
                    script.onerror = reject;
                    document.head.appendChild(script);
                });

                this.pyodide = await loadPyodide({
                    indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.24.1/full/'
                });

                this.pyodideLoaded = true;
                this.log('success', 'Python interpreter loaded!');
            } catch (error) {
                this.log('error', `Failed to load Python: ${error.message}`);
                return;
            }
        }

        try {
            // Redirect Python print to our console
            await this.pyodide.runPythonAsync(`
import sys
import io

class JSConsole:
    def write(self, text):
        if text.strip():
            print(text.strip())

    def flush(self):
        pass

sys.stdout = JSConsole()
sys.stderr = JSConsole()
            `);

            // Capture output
            const output = await this.pyodide.runPythonAsync(code);

            if (output !== undefined && output !== null) {
                this.log('success', String(output));
            }

            this.log('info', 'Python execution completed');
        } catch (error) {
            this.log('error', `Python Error: ${error.message}`);
        }
    }

    async runTypeScript(code) {
        this.log('info', 'Transpiling TypeScript...');

        try {
            // Simple TypeScript to JavaScript transpilation (removes type annotations)
            // For production, use actual TypeScript compiler
            const jsCode = code
                .replace(/:\s*(string|number|boolean|any|void|never)\s*/g, ' ')
                .replace(/interface\s+\w+\s*{[^}]*}/g, '')
                .replace(/type\s+\w+\s*=\s*[^;]+;/g, '')
                .replace(/as\s+(string|number|boolean|any)/g, '');

            this.log('info', 'Running transpiled JavaScript...');
            await this.runJavaScript(jsCode);
        } catch (error) {
            this.log('error', `TypeScript Error: ${error.message}`);
        }
    }

    log(type, message) {
        const output = document.getElementById('codeOutput');
        const line = document.createElement('div');
        line.className = `console-line console-${type}`;
        line.textContent = `[${type.toUpperCase()}] ${message}`;
        output.appendChild(line);
        output.scrollTop = output.scrollHeight;
    }

    clearConsole() {
        const output = document.getElementById('codeOutput');
        output.innerHTML = '<div class="console-line console-info">Ready to execute code...</div>';
    }

    async saveSnippet() {
        const code = document.getElementById('codeEditor').value;
        const language = document.getElementById('languageSelect').value;

        if (!code.trim()) {
            window.browser?.showToast('No code to save', 'error');
            return;
        }

        const name = prompt('Enter snippet name:') || `Snippet ${Date.now()}`;

        const snippet = {
            id: Date.now(),
            name,
            language,
            code,
            timestamp: Date.now()
        };

        this.snippets.push(snippet);
        this.saveSnippets();
        this.renderSnippets();
        window.browser?.showToast('Snippet saved!', 'success');
    }

    async loadSnippet() {
        if (this.snippets.length === 0) {
            window.browser?.showToast('No saved snippets', 'info');
            return;
        }

        // For simplicity, show a basic selection (in production, use a proper modal)
        const snippetNames = this.snippets.map((s, i) => `${i + 1}. ${s.name} (${s.language})`).join('\n');
        const selection = prompt(`Select snippet:\n${snippetNames}\n\nEnter number:`);

        if (selection) {
            const index = parseInt(selection) - 1;
            if (index >= 0 && index < this.snippets.length) {
                const snippet = this.snippets[index];
                document.getElementById('codeEditor').value = snippet.code;
                document.getElementById('languageSelect').value = snippet.language;
                window.browser?.showToast(`Loaded: ${snippet.name}`, 'success');
            }
        }
    }

    importCode() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.js,.ts,.py,.html,.txt';

        input.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (file) {
                const code = await file.text();
                document.getElementById('codeEditor').value = code;

                // Try to detect language from extension
                const ext = file.name.split('.').pop().toLowerCase();
                const langMap = {
                    'js': 'javascript',
                    'ts': 'typescript',
                    'py': 'python',
                    'html': 'html',
                    'htm': 'html'
                };

                if (langMap[ext]) {
                    document.getElementById('languageSelect').value = langMap[ext];
                }

                window.browser?.showToast(`Imported: ${file.name}`, 'success');
            }
        });

        input.click();
    }

    async loadSnippets() {
        const saved = localStorage.getItem('timelord_snippets');
        if (saved) {
            this.snippets = JSON.parse(saved);
            this.renderSnippets();
        }
    }

    saveSnippets() {
        localStorage.setItem('timelord_snippets', JSON.stringify(this.snippets));
    }

    renderSnippets() {
        const container = document.getElementById('snippetsList');

        if (this.snippets.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📝</div>
                    <div class="empty-state-text">No saved snippets</div>
                </div>
            `;
            return;
        }

        container.innerHTML = this.snippets.map(snippet => `
            <div class="snippet-item" data-snippet-id="${snippet.id}">
                <span class="snippet-icon">📝</span>
                <div class="snippet-info">
                    <div class="snippet-name">${snippet.name}</div>
                    <div class="snippet-lang">${snippet.language}</div>
                </div>
                <button class="snippet-delete" data-snippet-id="${snippet.id}">🗑️</button>
            </div>
        `).join('');

        // Add event listeners
        container.querySelectorAll('.snippet-item').forEach(item => {
            item.addEventListener('click', (e) => {
                if (!e.target.classList.contains('snippet-delete')) {
                    const id = parseInt(item.dataset.snippetId);
                    const snippet = this.snippets.find(s => s.id === id);
                    if (snippet) {
                        document.getElementById('codeEditor').value = snippet.code;
                        document.getElementById('languageSelect').value = snippet.language;
                        window.browser?.showToast(`Loaded: ${snippet.name}`, 'success');
                    }
                }
            });
        });

        container.querySelectorAll('.snippet-delete').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const id = parseInt(btn.dataset.snippetId);
                this.deleteSnippet(id);
            });
        });
    }

    deleteSnippet(id) {
        if (confirm('Delete this snippet?')) {
            this.snippets = this.snippets.filter(s => s.id !== id);
            this.saveSnippets();
            this.renderSnippets();
            window.browser?.showToast('Snippet deleted', 'success');
        }
    }

    clearAllSnippets() {
        if (confirm('Delete all snippets?')) {
            this.snippets = [];
            this.saveSnippets();
            this.renderSnippets();
            window.browser?.showToast('All snippets cleared', 'success');
        }
    }
}

// Initialize Code Runner when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.codeRunner = new CodeRunner();
});
