# A GUI line reordering tool

## Background

I am writing books and documents using Markdown, converting to PDF output. In this process
I use the Pandoc tool. I use the Pandoc command line option "${FILES[@]}" and to build that
FILES Bash variable I use a manifest file: `mapfile -t FILES < contents/manifest.txt`.

For more information on how I create books see [https://github.com/kevinpinscoe/how-I-make-books-now](https://github.com/kevinpinscoe/how-I-make-books-now)

Example:

```
pandoc \
  --metadata-file=metadata.yaml \
  --resource-path=contents \
  --from=markdown \
  --to=pdf \
  --pdf-engine=xelatex \
  --highlight-style=monochrome \
  -o "$OUT" \
  --toc --table-of-contents --toc-depth=2 \
  --top-level-division=chapter \
 --number-sections \
  "${FILES[@]}"
  ```

The Manifest file is a book order of file paths to Markdown content in the order I wish
for them to appear in the final book product (PDF).

Example:

```
contents/00-title/00-title-page.md
contents/chap01/section-a-title.md
contents/chap01/section-b-title.md
```

and so forth.

When I write I like to think in sections which I usually title as "## Section name" 
in Markdown. This allows me to edit the section and think about it easier with less clutter. 

To that end this tool allows me to re-order the manifest file visually while
thinking about how sections go together and in what order of precedence to put them.

## Install and operation

In my case Fedora Linux release 42:

```
sudo dnf install python3-pyside6

pip install --user PySide6` or `pip3 install --user PySide6

python line_reorder.py /full/path/to/your.txt
```

### Installing into ~/bin

Copy both files into `~/bin` and make the wrapper executable:

```bash
cp line_reorder.py ~/bin/
cp line-reorder ~/bin/
chmod +x ~/bin/line-reorder
```

Make sure `~/bin` is on your `PATH` (add this to `~/.bashrc` or `~/.bash_profile` if it isn't already):

```bash
export PATH="$HOME/bin:$PATH"
```

Then you can run it from anywhere:

```bash
line-reorder /full/path/to/your.txt
```

## What happens

A backup of the /full/path/to/your.txt will be saved with a date and time stamp 
for recovery purposes (`manifest.txt.20251008-121402.bak` for example) and the original file is updated in place.

## Contributing & Reporting Issues

Bug reports, feature requests, security disclosures, and contributions are all
welcome. I keep these guidelines in one place for all my projects:

- **How to contribute or report an issue:** https://github.com/kevinpinscoe/how-to-contribute
- **Report a security vulnerability:** do not open a public issue. Use the
  **"Report a vulnerability"** button on this repository's **Security** tab, or
  see the [security policy](https://github.com/kevinpinscoe/how-to-contribute/blob/main/SECURITY.md).
