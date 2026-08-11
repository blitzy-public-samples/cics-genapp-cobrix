******************************************************************
*  COPYBOOK  : GHLAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : LA
******************************************************************
 01  RT-HLA-RATING.

          03 RT-HLA-TERRITORY-CODE            PIC X(3).
          03 RT-HLA-CLASS-CODE                PIC X(4).
          03 RT-HLA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HLA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HLA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HLA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HLA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HLA-RATED-PREMIUM             PIC 9(9)V9(2).
