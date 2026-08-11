******************************************************************
*  COPYBOOK  : GFNHR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : NH
******************************************************************
 01  RT-FNH-RATING.

          03 RT-FNH-TERRITORY-CODE            PIC X(3).
          03 RT-FNH-CLASS-CODE                PIC X(4).
          03 RT-FNH-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FNH-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FNH-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FNH-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FNH-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FNH-RATED-PREMIUM             PIC 9(9)V9(2).
