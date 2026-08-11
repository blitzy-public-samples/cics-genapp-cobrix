******************************************************************
*  COPYBOOK  : GUTXR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : TX
******************************************************************
 01  RT-UTX-RATING.

          03 RT-UTX-TERRITORY-CODE            PIC X(3).
          03 RT-UTX-CLASS-CODE                PIC X(4).
          03 RT-UTX-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UTX-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UTX-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UTX-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UTX-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UTX-RATED-PREMIUM             PIC 9(9)V9(2).
