/*
 * Justin Ragatz
 *
 * 12 May 2016
 *
 * Simple program to feed parameters from OnRamp to HPL.dat.
 */
#include<stdlib.h>
#include<stdio.h>

int main (int argc, char** argv) {
    FILE* fp = NULL;

    fp = fopen("hpl-2.0/bin/BCCD/HPL.dat", "w");

    if (NULL == fp) {
	printf("Error: could not open file.\n");
	return -1;
    }

    if (argc < 8) {
	printf("Error: too few arguments.\n");
	return -1;
    }

    fprintf(fp, "HPLinpack benchmark input file\n"                   );
    fprintf(fp, "Bootable Cluster CD (http://bccd.net)\n"            );
    fprintf(fp, "HPL.out\t\toutput file name (if any)\n"             );
    fprintf(fp, "8\t\tdevice out (6=stdout,7=stderr,file)\n"         );
    fprintf(fp, "%s\t\t# of problems sizes (N)\n", argv[1]           );
    fprintf(fp, "%s\t\tNs\n", argv[2]                                );
    fprintf(fp, "%s\t\t# of NBs\n", argv[3]                          );
    fprintf(fp, "%s\t\tNBs\n", argv[4]                               );
    fprintf(fp, "0\t\tPMAP process mapping (0=Row-,1=Column-major)\n");
    fprintf(fp, "%s\t\t# of process grids (P x Q)\n", argv[5]        );
    fprintf(fp, "%s %s\t\tPs\n", argv[6]                             );
    fprintf(fp, "%s %s\t\tQs\n", argv[7]                             );
    fprintf(fp, "16.0\t\tthreshold\n"                                );
    fprintf(fp, "1\t\t# of panel fact\n"                             );
    fprintf(fp, "2\t\tPFACTs (0=left, 1=Crout, 2=Right)\n"           );
    fprintf(fp, "1\t\t# of recursive stopping criterium\n"           );
    fprintf(fp, "4\t\tNBMINs (>= 1)\n"                               );
    fprintf(fp, "1\t\t# of panels in recursion\n"                    );
    fprintf(fp, "2\t\tNDIVs\n"                                       );
    fprintf(fp, "1\t\t# of recursive panel fact.\n"                  );
    fprintf(fp, "1\t\tRFACTs (0=left, 1=Crout, 2=Right)\n"           );
    fprintf(fp, "1\t\t# of broadcast\n"                              );
    fprintf(fp, "1\t\tBCASTs (0=1rg,1=1rM,2=2rg,3=2rM,4=Lng,5=LnM)\n");
    fprintf(fp, "1\t\t# of lookahead depth\n"                        );
    fprintf(fp, "1\t\tDEPTHs (>=0)\n"                                );
    fprintf(fp, "2\t\tSWAP (0=bin-exch,1=long,2=mix)\n"              );
    fprintf(fp, "64\t\tswapping threshold\n"                         );
    fprintf(fp, "0\t\tL1 in (0=transposed,1=no-transposed) form\n"   );
    fprintf(fp, "0\t\tU  in (0=transposed,1=no-transposed) form\n"   );
    fprintf(fp, "1\t\tEquilibration (0=no,1=yes)\n"                  );
    fprintf(fp, "8\t\tmemory alignment in double (> 0)\n"            );

    fclose(fp);

    return 0;
}
