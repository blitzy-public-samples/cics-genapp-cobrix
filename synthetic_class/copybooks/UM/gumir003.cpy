******************************************************************
*  COPYBOOK  : GUMIR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : MI
******************************************************************
 01  RT-UMI-RATING.

          03 RT-UMI-TERRITORY-CODE            PIC X(3).
          03 RT-UMI-CLASS-CODE                PIC X(4).
          03 RT-UMI-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UMI-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UMI-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UMI-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UMI-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UMI-RATED-PREMIUM             PIC 9(9)V9(2).
