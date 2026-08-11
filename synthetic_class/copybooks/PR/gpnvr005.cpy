******************************************************************
*  COPYBOOK  : GPNVR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : NV
******************************************************************
 01  RT-PNV-RATING.

          03 RT-PNV-TERRITORY-CODE            PIC X(3).
          03 RT-PNV-CLASS-CODE                PIC X(4).
          03 RT-PNV-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PNV-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PNV-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PNV-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PNV-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PNV-RATED-PREMIUM             PIC 9(9)V9(2).
