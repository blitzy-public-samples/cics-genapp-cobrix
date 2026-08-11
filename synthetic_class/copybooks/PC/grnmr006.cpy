******************************************************************
*  COPYBOOK  : GRNMR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : NM
******************************************************************
 01  RT-RNM-RATING.

          03 RT-RNM-TERRITORY-CODE            PIC X(3).
          03 RT-RNM-CLASS-CODE                PIC X(4).
          03 RT-RNM-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-RNM-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-RNM-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-RNM-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-RNM-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-RNM-RATED-PREMIUM             PIC 9(9)V9(2).
