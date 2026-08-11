******************************************************************
*  COPYBOOK  : GURIR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : RI
******************************************************************
 01  RT-URI-RATING.

          03 RT-URI-TERRITORY-CODE            PIC X(3).
          03 RT-URI-CLASS-CODE                PIC X(4).
          03 RT-URI-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-URI-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-URI-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-URI-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-URI-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-URI-RATED-PREMIUM             PIC 9(9)V9(2).
