******************************************************************
*  COPYBOOK  : GPUTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : UT
******************************************************************
 01  RT-PUT-RATING.

          03 RT-PUT-TERRITORY-CODE            PIC X(3).
          03 RT-PUT-CLASS-CODE                PIC X(4).
          03 RT-PUT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PUT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PUT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PUT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PUT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PUT-RATED-PREMIUM             PIC 9(9)V9(2).
