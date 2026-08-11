******************************************************************
*  COPYBOOK  : GHSCR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : SC
******************************************************************
 01  RT-HSC-RATING.

          03 RT-HSC-TERRITORY-CODE            PIC X(3).
          03 RT-HSC-CLASS-CODE                PIC X(4).
          03 RT-HSC-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HSC-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HSC-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HSC-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HSC-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HSC-RATED-PREMIUM             PIC 9(9)V9(2).
