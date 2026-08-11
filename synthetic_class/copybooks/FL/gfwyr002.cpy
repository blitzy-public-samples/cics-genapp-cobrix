******************************************************************
*  COPYBOOK  : GFWYR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : WY
******************************************************************
 01  RT-FWY-RATING.

          03 RT-FWY-TERRITORY-CODE            PIC X(3).
          03 RT-FWY-CLASS-CODE                PIC X(4).
          03 RT-FWY-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FWY-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FWY-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FWY-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FWY-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FWY-RATED-PREMIUM             PIC 9(9)V9(2).
