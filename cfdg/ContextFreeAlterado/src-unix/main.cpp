/*
 *

 Context Free Design Grammar - version 0.1

 Copyright (C) 2005 Chris Coyne - ccoyne77@gmail.com

 [Send me anything cool you make with it or of it.]

 This program is free software; you can redistribute it and/or
 modify it under the terms of the GNU General Public License as published
 by the Free Software Foundation; either version 2 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program; if not, write to the Free Software
 Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
 02111-1307  USA

 *
 */

#include <iostream>
#include <sstream>
#include <fstream>
#include <time.h>
#ifdef _WIN32
#include "getopt.h"
#else
#include <unistd.h>
#endif
#include <stdlib.h>
#include "cfdg.h"
#include "variation.h"
#ifdef _WIN32
#include "WinPngCanvas.h"
#else
#include "pngCanvas.h"
#endif
#include "SVGCanvas.h"
#include "posixSystem.h"
#include "version.h"
#include "tiledCanvas.h"
#include "Rand48.h"
#include "makeCFfilename.h"

using namespace std;

void setupTimer(Renderer* renderer);

ostream* myCout = &cout;

const char* invokeName = "";

void
usage(bool inError)
{
  ostream& out = inError ? cerr : *myCout;

  out << APP_NAME(invokeName) << " - " << APP_VERSION() << "(v" << APP_BUILD() << ")" << endl;
  out << endl;
  out << "Usage: " << endl << APP_NAME(invokeName)
      << " [options] input.cfdg [output.png/svg]" << endl;
  out << "    or to pipe a cfdg file on standard input:" << endl;
  out << APP_NAME(invokeName)
      << " [options] - [output.png/svg]" << endl;
  out << "The output file name is omitted if the " << APP_OPTCHAR() << "o option is used" << endl << endl;
  out << "Options: " << endl;
  out << "    " << APP_OPTCHAR() <<
         "w num    width in pixels(png) or mm(svg) (default 500)" << endl;
  out << "    " << APP_OPTCHAR() <<
         "h num    height in pixels(png) or mm(svg) (default 500)" << endl;
  out << "    " << APP_OPTCHAR() <<
         "s num    set both width and height in pixels/mm" << endl;
  out << "    " << APP_OPTCHAR() <<
         "m num    maximum number of shapes (default none)" << endl;
  out << "    " << APP_OPTCHAR() <<
         "x float  minimum size of shapes in pixels/mm (default 0.3)" << endl;
  out << "    " << APP_OPTCHAR() <<
         "b float  border size [-1,2]: -1=-8 pixel border, 0=no border," << endl;
  out << "              1=8 pixel border, 2=variable-sized border" << endl;
  out << "    " << APP_OPTCHAR() <<
         "v str    set the variation code (default is random)" << endl;
  out << "    " << APP_OPTCHAR() <<
         "o str    set the output file name, supports variable expansion" << endl;
  out << "              %f expands to the animation frame number," << endl;
  out << "              %v and %V expands to the variation code in lower or upper case," << endl;
  out << "              %% expands to %" << endl;
  out << "    " << APP_OPTCHAR() <<
         "L        generate legacy big-endian variation" << endl;
  out << "    " << APP_OPTCHAR() <<
         "a num    generate num animation frames (PNG only)" << endl;
  out << "    " << APP_OPTCHAR() <<
         "z        zoom out during animation" << endl;
  out << "    " << APP_OPTCHAR() <<
         "V        generate SVG (vector) output" << endl;
  out << "    " << APP_OPTCHAR() <<
         "c        crop image output" << endl;
  out << "    " << APP_OPTCHAR() <<
         "q        quiet mode, suppress non-error output" << endl;
  out << "    " << APP_OPTCHAR() <<
         "t        time output, output the time taken to render the cfdg file" << endl;
  out << "    " << APP_OPTCHAR() <<
         "?        show this message, then exit" << endl;
  out << endl;

  exit(inError ? 2 : 0);
}

struct options {
  enum OutputFormat { PNGfile = 0, SVGfile = 1 };
  int   width;
  int   height;
  int   maxShapes;
  float minSize;
  float borderSize;

  int   variation;
  bool  legacyVariation;
  bool  crop;
  int   animationFrames;
  bool  animationZoom;

  const char* input;
  const char* output;
  const char* output_fmt;
  OutputFormat format;

  bool quiet;
  bool outputTime;
  
  options()
  : width(500), height(500), maxShapes(0), minSize(0.3F), borderSize(2.0F),
    variation(-1), legacyVariation(false), crop(false), animationFrames(0), 
    animationZoom(false), input(0), output(0), output_fmt(0), 
    format(PNGfile), quiet(false), outputTime(false)
  { }
};

int
intArg(char arg, const char* str)
{
  char* end;
  long int v = -1;

  v = strtol(str, &end, 10);
  if (end == str || v < 0) {
    if (arg == '-')
      cerr << "Argument must be a positive integer" << endl;
    else
      cerr << "Option -" << arg << " takes a positive integer argument" << endl;
    usage(true);
  }
  return (int)v;
}

float
floatArg(char arg, const char* str)
{
  float v = (float)atof(str);

  if (v < 0) {
    if (arg == '-')
      cerr << "Argument must be a positive float" << endl;
    else
      cerr << "Option -" << arg << " takes a positive float argument" << endl;
    usage(true);
  }
  return v;
}

void
processCommandLine(int argc, char* argv[], options& opt)
{
  extern char *optarg;
  extern int optind, optopt;

  invokeName = argv[0];

  int i;
  while ((i = getopt(argc, argv, ":w:h:s:N:m:x:b:v:a:o:cVzqtL?")) != -1) {
    char c = (char)i;
    switch(c) {
      case 'w':
        opt.width = intArg(c, optarg);
        break;
      case 'h':
        opt.height = intArg(c, optarg);
        break;
      case 's':
        opt.height = opt.width = intArg(c, optarg);
        break;
      case 'N':
	      opt.max_counter= intArg(c, optarg);
        break;
      case 'm':
        opt.maxShapes = intArg(c, optarg);
        break;
      case 'x':
        opt.minSize = floatArg(c, optarg);
        break;
      case 'b':
        opt.borderSize = (float)atof(optarg);
        if (opt.borderSize < -1 || opt.borderSize > 2) usage(true);
        break;
      case 'v':
        opt.variation = Variation::fromString(optarg);
        break;
      case 'o':
        opt.output_fmt = optarg;
        break;
      case 'L':
        opt.legacyVariation = true;
        break;
      case 'a':
        if (opt.format == options::SVGfile) usage(true);
        opt.animationFrames = intArg(c, optarg);
        break;
      case 'V':
        if (opt.animationFrames) usage(true);
        opt.format = options::SVGfile;
        break;
      case 'c':
        opt.crop = true;
        break;
      case 'z':
        opt.animationZoom = true;
        break;
      case ':':
        cerr << "Option -" << (char)optopt << " requires an argument" << endl;
        usage(true);
        break;
      case '?':
        if (optopt == '?')
          usage(false);
        cerr << "Unrecognized option: -" << optopt << endl;
        usage(true);
        break;
	  case 'q':
		opt.quiet = true;
		break;
	  case 't':
		opt.outputTime = true;
		break;
    }
  }

  if (optind < argc) {
    opt.input = argv[optind++];
  }
  if (optind < argc && !opt.output_fmt) {
    opt.output = argv[optind++];
  }
  if (optind < argc) {
    cerr << "Too many arguments" << endl;
    usage(true);
  }

  if (!opt.input) {
    cerr << "Missing input file" << endl;
    usage(true);
  }
  if (!opt.output && !opt.output_fmt) {
    cerr << "Missing output file" << endl;
    usage(true);
  }
}

class nullstreambuf : public streambuf
{
protected:
	int overflow(int c) { return c; }
};
class nullostream : public ostream
{
public:
	nullostream() : ostream (new nullstreambuf()) {}
};


int main (int argc, char* argv[]) {
  options opts;
  int var = Variation::random(6);

  processCommandLine(argc, argv, opts);

  if (opts.quiet) myCout = new nullostream();

  clock_t startTime = clock();
  clock_t fromTime = startTime;
  clock_t clocksPerMsec = CLOCKS_PER_SEC / 1000;
  
  Rand48::BigEndian = opts.legacyVariation;

  if (opts.variation < 0) opts.variation = var;
  char code[Variation::maxStringLength];
  Variation::toString(opts.variation, code, false);
  
  PosixSystem system(opts.quiet);;
  CFDG* myDesign = CFDG::ParseFile(opts.input, &system, opts.variation);
  if (!myDesign) return 1;

  agg::trans_affine tileTransform;
  bool isTiled = myDesign->isTiled(&tileTransform);
  
  // If a static output file name is provided then generate an output
  // file name format string by escaping any '%' characters. If this is 
  // an animation run then add "_%f" before the extension.
  string newOutput;
  if (!opts.output_fmt) {
    stringstream namestream(stringstream::out);
    const char* p = opts.output;
    const char* ext = strrchr(opts.output, '.');
    bool hasExt = ext && ext > strrchr(opts.output, '/');
    while (*p) {
      const char* perc = strchr(p, '%');
      if (perc && perc < ext) {
        namestream.write(p, perc - p);
        namestream << "%%";
        p = perc + 1;
        continue;
      }
      if (hasExt && opts.animationFrames) {
        namestream.write(p, ext - p);
        namestream << "_%f";
        p = ext + 1;
        hasExt = false;
        continue;
      }
      namestream << p;
      break;
    }
    if (!hasExt && opts.animationFrames) 
        namestream << "_%f";
    newOutput = namestream.str();
    opts.output_fmt = newOutput.c_str();
  }

  bool useRGBA = myDesign->usesColor;
  aggCanvas::PixelFormat pixfmt = aggCanvas::SuggestPixelFormat(myDesign);

  *myCout << "Generating " << (useRGBA ? "color" : "gray-scale")
          << ((opts.format == options::PNGfile) ? 
            " PNG image" : " SVG vector output") 
          << (opts.legacyVariation ? ", legacy variation " : ", variation ") 
          << code << "..." << endl;

  pngCanvas* png = 0;
  SVGCanvas* svg = 0;
  tiledCanvas* tile = 0;
  Canvas* myCanvas;
  
  Renderer* myRenderer = myDesign->renderer(
                                            opts.width, opts.height, opts.minSize,
                                            opts.variation, opts.borderSize);
  myRenderer->setMaxShapes(opts.maxShapes);
  opts.width = myRenderer->m_width;
  opts.height = myRenderer->m_height;
  printf ("%d\n",opts.max_counter);
  double scale = myRenderer->run(0, false, opts.max_counter);
  
  if (system.error())
      return 5;

  if (opts.outputTime) {
	  clock_t toTime = clock();
	  clock_t runTime = (toTime - fromTime) / clocksPerMsec;
	  *myCout << "The cfdg file took " << runTime << " msec to execute." << endl;
      fromTime = toTime;
  }
  
  if (opts.format == options::PNGfile) {
      png = new pngCanvas(opts.output_fmt, opts.quiet, opts.width, opts.height, pixfmt, opts.crop, opts.animationFrames, opts.variation);
	  myCanvas = (Canvas*)png;
  } else {
      string name = makeCFfilename(opts.output_fmt, 0, 0, opts.variation);
	  svg = new SVGCanvas(name.c_str(), opts.width, opts.height, opts.crop);
	  myCanvas = (Canvas*)svg;
  }
  
  if (isTiled) {
      tile = new tiledCanvas(myCanvas, tileTransform);
      myCanvas = tile;
      tile->scale(scale);
  }

  if (!opts.quiet) setupTimer(myRenderer);

  if (opts.animationFrames) {
    myRenderer->animate(myCanvas, opts.animationFrames, opts.animationZoom);
  } else {
    myRenderer->draw(myCanvas);
  }
  *myCout << endl;

  if (!opts.quiet) setupTimer(0);
  
  *myCout << "DONE!" << endl;
  *myCout << "The output file name is " << 
    makeCFfilename(opts.output_fmt, 0, 0, opts.variation) << endl;

  if (opts.outputTime) {
	  clock_t toTime = clock();
	  clock_t runTime = (toTime - fromTime) / clocksPerMsec;
	  *myCout << "The cfdg file took " << runTime << " msec to render." << endl;
	  runTime = (toTime - startTime) / clocksPerMsec;
	  *myCout << "The cfdg file took a total of " << runTime << " msec to process." << endl;
  }
  
  
  delete png;
  delete svg;
  delete tile;

  return 0;
}


