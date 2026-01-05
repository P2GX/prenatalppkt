# Internal

Tips for development of the resource



```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate   # (or 'venv\Scripts\activate' on Windows)

# 2. Upgrade pip and setuptools
pip install --upgrade pip setuptools wheel

# 3. Install MkDocs core
pip install mkdocs>=1.6,<2.0

# 4. Install Material for MkDocs (with emoji/imaging support)
pip install "mkdocs-material[imaging]>=9.5.10,<10"
pip install mkdocs-material-extensions>=1.3,<2.0

# 5. Install Markdown extensions used in mkdocs.yml
pip install "pymdown-extensions>=10.0,<11"

# 6. Install MkDocStrings and helpers for Python API docs
pip install "mkdocstrings[python]>=0.22,<1.0"
pip install "mkdocs-autorefs>=1.4,<2.0"

# 7. Install Markdown include and diagram plugins
pip install "mkdocs-include-markdown-plugin>=7.2.0,<8.0"
pip install "mkdocs-mermaid2-plugin>=1.2,<2.0"

# 8. Install dynamic file generator plugin
pip install "mkdocs-gen-files>=0.5.0,<1.0"

# 9. Install optional render/image support for emoji, diagrams, etc.
pip install pillow cairosvg

# 10. Confirm everything works
mkdocs --version
mkdocs serve
```
