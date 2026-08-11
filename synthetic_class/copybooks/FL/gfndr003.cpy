******************************************************************
*  COPYBOOK  : GFNDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : ND
******************************************************************
 01  RT-FND-RATING.

          03 RT-FND-TERRITORY-CODE            PIC X(3).
          03 RT-FND-CLASS-CODE                PIC X(4).
          03 RT-FND-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FND-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FND-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FND-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FND-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FND-RATED-PREMIUM             PIC 9(9)V9(2).
