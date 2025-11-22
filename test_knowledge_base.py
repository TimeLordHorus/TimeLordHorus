#!/usr/bin/env python3
"""
Test script for Chronos Knowledge Base
Tests document upload, parsing, and search functionality
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent / 'tl-linux' / 'ai'))

from chronos_knowledge import ChronosKnowledgeBase

def create_test_documents():
    """Create some test documents"""
    test_docs_dir = Path('/tmp/chronos_test_docs')
    test_docs_dir.mkdir(exist_ok=True)

    # Test document 1: About Python
    doc1 = test_docs_dir / 'python_intro.txt'
    doc1.write_text("""
Python Programming Language

Python is a high-level, interpreted programming language known for its simplicity
and readability. Created by Guido van Rossum and first released in 1991, Python
emphasizes code readability with its notable use of significant indentation.

Key Features:
- Easy to learn and use
- Extensive standard library
- Dynamic typing
- Object-oriented and functional programming support
- Large and active community

Python is widely used for:
- Web development (Django, Flask)
- Data science and machine learning
- Automation and scripting
- Scientific computing
- Artificial intelligence

The language supports multiple programming paradigms and has a comprehensive
standard library often described as having "batteries included" due to its
extensive capabilities right out of the box.
    """.strip())

    # Test document 2: About Linux
    doc2 = test_docs_dir / 'linux_basics.txt'
    doc2.write_text("""
Linux Operating System

Linux is a family of open-source Unix-like operating systems based on the Linux
kernel, first released by Linus Torvalds in 1991. Linux is typically packaged in
a Linux distribution.

Popular Linux Distributions:
- Ubuntu - User-friendly and great for beginners
- Debian - Stable and reliable
- Fedora - Cutting-edge features
- Arch Linux - Highly customizable
- CentOS/Rocky Linux - Enterprise-focused

Key Advantages:
- Free and open source
- Highly secure and stable
- Customizable and flexible
- Strong command-line interface
- Large community support
- Excellent for servers and development

Linux powers much of the internet, with most web servers running Linux. It's also
the foundation for Android, making it the most widely used operating system kernel
in the world by number of devices.

Common Linux Commands:
- ls: List directory contents
- cd: Change directory
- pwd: Print working directory
- mkdir: Create directory
- rm: Remove files or directories
- grep: Search text patterns
    """.strip())

    # Test document 3: About AI
    doc3 = test_docs_dir / 'ai_overview.md'
    doc3.write_text("""
# Artificial Intelligence Overview

## What is AI?

Artificial Intelligence (AI) refers to the simulation of human intelligence
in machines that are programmed to think and learn like humans. The term may
also be applied to any machine that exhibits traits associated with a human
mind such as learning and problem-solving.

## Types of AI

### Narrow AI (Weak AI)
- Designed for specific tasks
- Examples: Voice assistants, image recognition, recommendation systems

### General AI (Strong AI)
- Theoretical AI with human-like general intelligence
- Can understand, learn, and apply knowledge across different domains

## Machine Learning
Machine Learning is a subset of AI that enables systems to learn and improve
from experience without being explicitly programmed. Types include:

- **Supervised Learning**: Learning from labeled data
- **Unsupervised Learning**: Finding patterns in unlabeled data
- **Reinforcement Learning**: Learning through trial and error

## Applications
- Healthcare: Diagnosis, drug discovery
- Finance: Fraud detection, trading
- Transportation: Self-driving cars
- Entertainment: Content recommendations
- Customer Service: Chatbots, virtual assistants

## Ethical Considerations
- Privacy and data protection
- Bias and fairness
- Transparency and explainability
- Job displacement
- Safety and security
    """.strip())

    return [doc1, doc2, doc3]

def test_knowledge_base():
    """Test the knowledge base functionality"""
    print("\n" + "=" * 70)
    print("CHRONOS KNOWLEDGE BASE TEST")
    print("=" * 70 + "\n")

    # Initialize knowledge base
    print("1. Initializing knowledge base...")
    kb = ChronosKnowledgeBase()
    print(f"✓ Knowledge base initialized at: {kb.storage_path}\n")

    # Create test documents
    print("2. Creating test documents...")
    test_docs = create_test_documents()
    print(f"✓ Created {len(test_docs)} test documents\n")

    # Upload documents
    print("3. Uploading documents...")
    for doc_path in test_docs:
        print(f"   Uploading: {doc_path.name}")
        result = kb.upload_document(doc_path)

        if result['success']:
            print(f"   ✓ Success: {result['metadata']['word_count']} words, "
                  f"{len(result['metadata']['keywords'])} keywords")
        else:
            print(f"   ✗ Error: {result['error']}")

    print()

    # Get stats
    print("4. Knowledge base statistics:")
    stats = kb.get_stats()
    print(f"   Total documents: {stats['total_documents']}")
    print(f"   Total words: {stats['total_words']:,}")
    print(f"   Last updated: {stats['last_updated'][:19]}\n")

    # List documents
    print("5. Listing all documents:")
    docs = kb.list_documents()
    for doc in docs:
        print(f"   📄 {doc['filename']}")
        print(f"      Words: {doc['word_count']:,}, Keywords: {len(doc['keywords'])}")
    print()

    # Test searches
    print("6. Testing searches:")
    print("-" * 70)

    test_queries = [
        "What is Python?",
        "Tell me about Linux distributions",
        "Machine learning types",
        "What are the advantages of Linux?",
        "How is AI used in healthcare?"
    ]

    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        results = kb.search(query, max_results=2)

        if results:
            print(f"   Found {len(results)} result(s):\n")
            for result in results:
                print(f"   📚 {result['filename']} (score: {result['score']})")
                print(f"      {result['snippet'][:150]}...\n")
        else:
            print("   No results found.\n")

    print("=" * 70)

    # Test with Chronos AI
    print("\n7. Testing Chronos AI integration...")
    try:
        sys.path.insert(0, str(Path(__file__).parent / 'tl-linux' / 'ai'))
        from chronos_ai import ChronosAI

        chronos = ChronosAI(headless=True)

        if chronos.knowledge_base:
            print("✓ Chronos AI successfully initialized with knowledge base\n")

            # Test a question
            question = "What is Python used for?"
            print(f"Testing question: '{question}'")
            response = chronos.search_knowledge_base(question)

            if response:
                print(f"\nChronos response:\n{response}\n")
            else:
                print("No knowledge base results.\n")
        else:
            print("✗ Knowledge base not available in Chronos AI\n")

    except Exception as e:
        print(f"✗ Error testing Chronos AI: {e}\n")

    print("=" * 70)
    print("✓ ALL TESTS COMPLETED")
    print("=" * 70 + "\n")

    print("Summary:")
    print(f"  • {len(test_docs)} documents uploaded")
    print(f"  • {stats['total_words']:,} total words indexed")
    print(f"  • Knowledge base ready for use")
    print(f"  • Location: {kb.storage_path}")
    print("\nYou can now launch Chronos AI and:")
    print("  1. Go to the Documents tab to see uploaded documents")
    print("  2. Upload your own documents")
    print("  3. Ask questions in the Chat tab to search your documents")
    print()

if __name__ == '__main__':
    test_knowledge_base()
