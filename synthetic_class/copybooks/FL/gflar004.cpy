******************************************************************
*  COPYBOOK  : GFLAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : LA
******************************************************************
 01  RT-FLA-RATING.

          03 RT-FLA-TERRITORY-CODE            PIC X(3).
          03 RT-FLA-CLASS-CODE                PIC X(4).
          03 RT-FLA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FLA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FLA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FLA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FLA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FLA-RATED-PREMIUM             PIC 9(9)V9(2).
