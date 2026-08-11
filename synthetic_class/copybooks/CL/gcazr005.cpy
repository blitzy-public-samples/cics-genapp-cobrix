******************************************************************
*  COPYBOOK  : GCAZR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : AZ
******************************************************************
 01  RT-CAZ-RATING.

          03 RT-CAZ-TERRITORY-CODE            PIC X(3).
          03 RT-CAZ-CLASS-CODE                PIC X(4).
          03 RT-CAZ-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CAZ-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CAZ-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CAZ-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CAZ-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CAZ-RATED-PREMIUM             PIC 9(9)V9(2).
