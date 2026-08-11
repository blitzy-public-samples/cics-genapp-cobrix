******************************************************************
*  COPYBOOK  : GUFLR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : FL
******************************************************************
 01  RT-UFL-RATING.

          03 RT-UFL-TERRITORY-CODE            PIC X(3).
          03 RT-UFL-CLASS-CODE                PIC X(4).
          03 RT-UFL-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UFL-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UFL-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UFL-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UFL-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UFL-RATED-PREMIUM             PIC 9(9)V9(2).
