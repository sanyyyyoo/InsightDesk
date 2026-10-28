// ============================================================================
//  SAMPLE CHAPTER 4 — Citing references
//  Read the compiled PDF side-by-side with this file.
// ============================================================================

#import "/template/tutorial.typ": *

= Citing References

== Adding a Reference

The template makes the Bibliography at the end of the book for you, in IEEE style. You only collect your references in a `.bib` file and cite them in your text. To add a reference:

+ Search for the paper or book on #link("https://scholar.google.com")[Google Scholar].
+ Click *Cite* under the result, then *BibTeX*, and copy the text that appears.
+ Paste it at the end of the right file in `content/references/`:
  - `books.bib` for books (listed under "Books" in the Bibliography),
  - `journals.bib` for journal and conference papers, websites and everything else.

A BibTeX entry looks like this:

#code(```bib
@article{lecun2015deep,
  author  = {Yann LeCun and Yoshua Bengio and Geoffrey Hinton},
  title   = {Deep Learning},
  journal = {Nature},
  volume  = {521},
  pages   = {436--444},
  year    = {2015},
}
```)

The word right after `@article{`, here `lecun2015deep`, is the entry's *key*. You use it to cite the entry. You can change it to anything easy to remember, as long as no two entries have the same key.

== Citing in Your Text

Write `@` followed by the key:

#example(```typ
Deep learning has transformed computer vision @lecun2015deep.
Modern information theory began with Shannon @shannon1948mathematical.
Several works can be cited together @lecun2015deep @einstein1905electrodynamics.
```)

The numbers in square brackets match the numbered list in the Bibliography at the end of the book.

== Citing Websites

For a website, add an `@online` entry to `journals.bib`:

#code(```bib
@online{pytorch-docs,
  title   = {PyTorch Documentation},
  author  = {{PyTorch Contributors}},
  url     = {https://pytorch.org/docs/stable/},
  urldate = {2026-01-15},
}
```)

== Good Practice

- *Every* entry in the `.bib` files is printed in the Bibliography, whether you cite it or not. Delete the sample entries that came with this template, and any you don't use.
- If you use a figure or table from someone else's work, cite it in the caption, for example `caption: [ResNet architecture @he2016deep]`.
- Check what Google Scholar gives you. Its BibTeX sometimes has missing page numbers or names in the wrong case.
