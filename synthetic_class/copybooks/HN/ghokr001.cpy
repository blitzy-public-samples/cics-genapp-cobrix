******************************************************************
*  COPYBOOK  : GHOKR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : OK
******************************************************************
 01  RT-HOK-RATING.

          03 RT-HOK-TERRITORY-CODE            PIC X(3).
          03 RT-HOK-CLASS-CODE                PIC X(4).
          03 RT-HOK-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HOK-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HOK-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HOK-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HOK-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HOK-RATED-PREMIUM             PIC 9(9)V9(2).
