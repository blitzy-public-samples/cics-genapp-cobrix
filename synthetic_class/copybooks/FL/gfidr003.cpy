******************************************************************
*  COPYBOOK  : GFIDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : ID
******************************************************************
 01  RT-FID-RATING.

          03 RT-FID-TERRITORY-CODE            PIC X(3).
          03 RT-FID-CLASS-CODE                PIC X(4).
          03 RT-FID-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FID-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FID-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FID-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FID-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FID-RATED-PREMIUM             PIC 9(9)V9(2).
