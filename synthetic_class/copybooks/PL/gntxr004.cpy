******************************************************************
*  COPYBOOK  : GNTXR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : TX
******************************************************************
 01  RT-NTX-RATING.

          03 RT-NTX-TERRITORY-CODE            PIC X(3).
          03 RT-NTX-CLASS-CODE                PIC X(4).
          03 RT-NTX-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NTX-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NTX-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NTX-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NTX-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NTX-RATED-PREMIUM             PIC 9(9)V9(2).
