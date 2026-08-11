******************************************************************
*  COPYBOOK  : GHNCR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : NC
******************************************************************
 01  RT-HNC-RATING.

          03 RT-HNC-TERRITORY-CODE            PIC X(3).
          03 RT-HNC-CLASS-CODE                PIC X(4).
          03 RT-HNC-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HNC-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HNC-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HNC-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HNC-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HNC-RATED-PREMIUM             PIC 9(9)V9(2).
