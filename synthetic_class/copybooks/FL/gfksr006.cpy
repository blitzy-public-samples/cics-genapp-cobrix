******************************************************************
*  COPYBOOK  : GFKSR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : KS
******************************************************************
 01  RT-FKS-RATING.

          03 RT-FKS-TERRITORY-CODE            PIC X(3).
          03 RT-FKS-CLASS-CODE                PIC X(4).
          03 RT-FKS-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FKS-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FKS-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FKS-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FKS-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FKS-RATED-PREMIUM             PIC 9(9)V9(2).
