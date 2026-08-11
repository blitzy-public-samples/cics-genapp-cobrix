******************************************************************
*  COPYBOOK  : GUNJR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : NJ
******************************************************************
 01  RT-UNJ-RATING.

          03 RT-UNJ-TERRITORY-CODE            PIC X(3).
          03 RT-UNJ-CLASS-CODE                PIC X(4).
          03 RT-UNJ-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UNJ-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UNJ-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UNJ-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UNJ-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UNJ-RATED-PREMIUM             PIC 9(9)V9(2).
