******************************************************************
*  COPYBOOK  : GUNMR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : NM
******************************************************************
 01  RT-UNM-RATING.

          03 RT-UNM-TERRITORY-CODE            PIC X(3).
          03 RT-UNM-CLASS-CODE                PIC X(4).
          03 RT-UNM-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UNM-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UNM-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UNM-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UNM-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UNM-RATED-PREMIUM             PIC 9(9)V9(2).
