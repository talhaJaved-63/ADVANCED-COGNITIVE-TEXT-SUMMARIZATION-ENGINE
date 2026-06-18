import sys
from summarizer import summarize

def main():
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        print("Paste your text (Ctrl+Z then Enter to finish):")
        text = sys.stdin.read().strip()

    if not text:
        print("No text provided.")
        sys.exit(1)

    result = summarize(text)
    print("\n--- Summary ---\n")
    print(result)

if __name__ == "__main__":
    main()
