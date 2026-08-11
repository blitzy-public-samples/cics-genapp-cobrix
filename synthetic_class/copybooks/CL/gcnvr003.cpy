******************************************************************
*  COPYBOOK  : GCNVR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : NV
******************************************************************
 01  RT-CNV-RATING.

          03 RT-CNV-TERRITORY-CODE            PIC X(3).
          03 RT-CNV-CLASS-CODE                PIC X(4).
          03 RT-CNV-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CNV-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CNV-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CNV-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CNV-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CNV-RATED-PREMIUM             PIC 9(9)V9(2).
