******************************************************************
*  COPYBOOK  : GUDER001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : DE
******************************************************************
 01  RT-UDE-RATING.

          03 RT-UDE-TERRITORY-CODE            PIC X(3).
          03 RT-UDE-CLASS-CODE                PIC X(4).
          03 RT-UDE-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UDE-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UDE-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UDE-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UDE-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UDE-RATED-PREMIUM             PIC 9(9)V9(2).
