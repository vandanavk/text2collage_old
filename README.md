# text2collage

This library converts a given paragraph of text into an equivalent image illustration, represented as a collage of images. It also gives the user the option of creating a collage of images from a folder containing a set of images.

usage: text2collage.py [-h] [-o {text,collection}] [-d D] [-cw CW] [-ch CH] [-i {random,auto,user}] [-b B] [-GA GA GA GA GA GA]

arguments:

  -h, --help 	    show this help message and exit
  
  -o {text,collection}  			Option ‘text’ - convert text to a collage of images. Option ‘collection’ - create a collage from a collection of images
  
  -d D                  				Absolute path of folder containing text input (if text to collage is chosen) or folder containing images (if image collection to collage is chosen). This argument is mandatory.
  
  -cw CW                				Width of collage canvas
  
  -ch CH                				Height of collage canvas
  
  -i {random,auto,user}			Importance estimator for the images in the collage. The importance assigned, will help the library decide the scale of each image in the collage. 
  
  'random' - randomly assigned scale between 1 and 5
  
  'auto' - used when text is converted to collage. Importance is computed from phrase score.
	
   'user' - User-specified importance value scaled down to the range 1-5
  
  -b B                  				Space between images in the collage (in pixels)
  
  -GA ngen npop Pc Pm lam    	GA parameters - number of iterations, population size,crossover probability, mutation probability, lambda (fitness function parameter - lam)



References:
* Steven Bird, Ewan Klein, and Edward Loper. 2009. Natural Language Processing with Python (1st ed.). O’Reilly Media, Inc.
* J. Fan. 2012. Photo Layout with a Fast Evaluation Method and Genetic Algorithm. In 2012 IEEE International Conference on Multimedia and Expo Workshops. 308–313. DOI:h p://dx.doi.org/10.1109/ICMEW.2012.59 
* Fe ́lix-Antoine Fortin, Francois-Michel De Rainville, Marc-Andre ́ Gardner, Marc Parizeau, and Christian Gagne ́. 2012. DEAP: Evolutionary Algorithms Made Easy. Journal of Machine Learning Research 13 (jul 2012), 2171–2175. 
* Weizhi Meng. 2015. A sentence-based image search engine. Master’s thesis. Missouri University of Science and Technology. 
* Bob Coyne and Richard Sproat. 2001. WordsEye: An Automatic Text-to-scene Conversion System. In Proceedings of the 28th Annual Conference on Computer Graphics and Interactive Techniques (SIGGRAPH ’01). ACM, New York, NY, USA, 487–496. DOI:h p://dx.doi.org/10.1145/383259.383316 
* Andrew B. Goldberg, Xiaojin Zhu, Charles R. Dyer, Mohamed Eldawy, and Lijie Heng. 2008. Easy as ABC? Facilitating Pictorial Communication via Semantically Enhanced Layout. In Proceedings of the Twelfth Conference on Computational Natural Language Learning, CoNLL 2008, Manchester, UK, August 16-17, 2008. 119–126. h p://aclweb.org/anthology/W/W08/W08- 2116.pdf 
* S.J. Rose, W.E. Cowley, V.L. Crow, and N.O. Cramer. 2012. Rapid automatic keyword extraction for information retrieval and analysis. (March 6 2012). h ps://www.google.com/patents/US8131735 US Patent 8,131,735. 
* Xiaojin Zhu, Andrew B. Goldberg, Mohamed Eldawy, Charles R. Dyer, and Bradley Strock. 2007. A Text-to-Picture Synthesis System for Augmenting Com- munication. In Proceedings of the Twenty-Second AAAI Conference on Arti cial Intelligence, July 22-26, 2007, Vancouver, British Columbia, Canada. 1590–1596. h p://www.aaai.org/Library/AAAI/2007/aaai07- 252.php  
