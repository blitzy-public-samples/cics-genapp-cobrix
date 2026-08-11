******************************************************************
*  COPYBOOK  : GFNYR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : NY
******************************************************************
 01  RT-FNY-RATING.

          03 RT-FNY-TERRITORY-CODE            PIC X(3).
          03 RT-FNY-CLASS-CODE                PIC X(4).
          03 RT-FNY-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FNY-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FNY-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FNY-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FNY-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FNY-RATED-PREMIUM             PIC 9(9)V9(2).
