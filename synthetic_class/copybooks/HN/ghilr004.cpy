******************************************************************
*  COPYBOOK  : GHILR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : IL
******************************************************************
 01  RT-HIL-RATING.

          03 RT-HIL-TERRITORY-CODE            PIC X(3).
          03 RT-HIL-CLASS-CODE                PIC X(4).
          03 RT-HIL-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HIL-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HIL-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HIL-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HIL-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HIL-RATED-PREMIUM             PIC 9(9)V9(2).
