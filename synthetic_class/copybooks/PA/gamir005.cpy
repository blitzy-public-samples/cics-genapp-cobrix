******************************************************************
*  COPYBOOK  : GAMIR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : MI
******************************************************************
 01  RT-AMI-RATING.

          03 RT-AMI-TERRITORY-CODE            PIC X(3).
          03 RT-AMI-CLASS-CODE                PIC X(4).
          03 RT-AMI-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-AMI-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-AMI-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-AMI-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-AMI-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-AMI-RATED-PREMIUM             PIC 9(9)V9(2).
