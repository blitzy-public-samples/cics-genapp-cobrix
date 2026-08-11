******************************************************************
*  COPYBOOK  : GUKSR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : KS
******************************************************************
 01  RT-UKS-RATING.

          03 RT-UKS-TERRITORY-CODE            PIC X(3).
          03 RT-UKS-CLASS-CODE                PIC X(4).
          03 RT-UKS-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UKS-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UKS-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UKS-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UKS-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UKS-RATED-PREMIUM             PIC 9(9)V9(2).
