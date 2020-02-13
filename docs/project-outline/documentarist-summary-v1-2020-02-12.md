# Documentarist project summary

Michael Hucka<br>
Version 1 (2020-02-12)

## Project goals

The goal of _Documentarist_ is to create a software system to process digital document and photo archives at the Caltech Library, and annotate each document page with information about its contents.  The initial focus will be to perform automated text recognition and object recognition using machine learning techniques, and then add metadata to the documents with the inferred contents. Once this is achieved, the framework may be expanded to perform other automated data processing tasks. The output will be fed back to the Caltech Archives' online collections to enhance search and enrich the contents.

## Documentarist requirements analysis

The general requirements are relatively straightforward:

1. Accept as input a set of paths to directories containing images, and/or lists of URLs.
2. Read each document image and perform analysis tasks. Processing should be performed in parallel as much as possible, and (for cost efficiency) should minimize network service invocations to paid services from Microsoft, Google, and/or other vendors used.
3. Write the results of the analysis to files that correspond go the input files, in two formats:  
    a) hOCR, to display recognized text over the printed and handwritten text of a document page  
    b) JSON, to provide all extracted data in a simple format for further processing.

Getting the results of the processes back into the Caltech Archives Islandora system will take an additional step whose details are not fully worked out at this time. The process can reasonably be assumed to involve taking the output data and processing it in some suitable way to store it into Islandora. This will require writing some kind of custom but straightforward adapter program(s).

## Initial Documentarist architecture

The basic software architecture envisioned at this time involves a modular processing pipeline:

1. Read (and possibly store locally) each input file.
2. Apply several modules to preprocess the images and perform analysis tasks:  
    * _Cropper_: automatically crop excessive white space around document images.
    * _Text Describer_: apply text recognition and other processes to determine whether an input document contains handwritten or printed text or both, and if it does, extract the text.
    * _Figure Describer_: identify any figures in the input, whether that be photos, drawings or graphs.
    * _Content Describer_: compute additional metadata over the input document, such as performing entity recognition on the results, performing object recognition in images, etc.
    * _Date Spotter_: detect the presence of dates written in or on the document page and extract them.
3. Write text in hOCR format, and also write all metadata and text in a JSON format.

## Future directions

Having achived the above, we will be in a position to do other analysis on the results. For example, we could try topic modeling over individual or multiple document pages; similarly, it may be possible to recognize specific entities or people and automatically link them to (e.g.) Caltech people's pages, Wikipedia pages, etc.
