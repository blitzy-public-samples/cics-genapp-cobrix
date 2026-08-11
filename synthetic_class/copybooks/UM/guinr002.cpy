******************************************************************
*  COPYBOOK  : GUINR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : IN
******************************************************************
 01  RT-UIN-RATING.

          03 RT-UIN-TERRITORY-CODE            PIC X(3).
          03 RT-UIN-CLASS-CODE                PIC X(4).
          03 RT-UIN-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UIN-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UIN-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UIN-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UIN-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UIN-RATED-PREMIUM             PIC 9(9)V9(2).
